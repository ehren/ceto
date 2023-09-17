import typing
from typing import Union, Any

from .semanticanalysis import NamedParameter, IfWrapper, SemanticAnalysisError, \
    SyntaxTypeOp, find_use, find_uses, find_all, is_return, is_void_return, \
    Scope, ClassDefinition, InterfaceDefinition, creates_new_variable_scope, \
    LocalVariableDefinition, ParameterDefinition, type_node_to_list_of_types, \
    list_to_typed_node, list_to_attribute_access_node, is_call_lambda
from .abstractsyntaxtree import Node, Module, Call, Block, UnOp, BinOp, TypeOp, Assign, Identifier, ListLiteral, TupleLiteral, BracedLiteral, ArrayAccess, BracedCall, StringLiteral, AttributeAccess, Template, ArrowOp, ScopeResolution, LeftAssociativeUnOp, IntegerLiteral

from collections import defaultdict
import re


mut_by_default = False


class CodeGenError(Exception):
    pass


cpp_preamble = r"""
#include <string>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <sstream>
#include <functional>
#include <cassert>
#include <compare> // for <=>
#include <thread>
#include <optional>

//#include <concepts>
//#include <ranges>
//#include <numeric>


#include "ceto.h"

"""


# Uses code and ideas from https://github.com/lukasmartinelli/py14

# method_declarations = []
cstdlib_functions = ["printf", "fprintf", "fopen", "fclose"]
counter = 0


def gensym(prefix=None):
    global counter
    counter += 1
    pre = "_ceto_private_"
    if prefix is not None:
        pre += prefix
    return pre + str(counter)


def codegen_if(ifcall : Call, cx):
    assert isinstance(ifcall, Call)
    assert ifcall.func.name == "if" 

    ifkind = ifcall.declared_type

    indt = cx.indent_str()
    cpp = ""

    is_expression = not isinstance(ifcall.parent, Block)

    if is_expression:
        if any(find_all(ifcall, is_return, stop=creates_new_variable_scope)):
            raise CodeGenError("no explicit return in if expression", ifcall)

        for a in ifcall.args:
            if isinstance(a, Block):
                last_statement = a.args[-1]
                synthetic_return = SyntaxTypeOp(func=":", args=[Identifier("return", source=None), last_statement], source=None)
                last_statement.parent = synthetic_return
                a.args = a.args[0:-1] + [synthetic_return]

    ifnode = IfWrapper(ifcall.func, ifcall.args)

    if ifkind is not None and ifkind.name == "noscope":
        # python-style "noscope" ifs requires a specifier

        if is_expression or not cx.in_function_body:
            raise CodeGenError("unscoped if disallowed in expression context", ifcall)

        # scopes = [ifnode.cond, ifnode.thenblock]
        scopes = [ifnode.thenblock]
        if ifnode.elseblock is not None:
            scopes.append(ifnode.elseblock)
        else:
            raise CodeGenError("unscoped if without else block disallowed", ifcall)

        for elifcond, elifblock in ifnode.eliftuples:
            # scopes.append(elifcond)
            scopes.append(elifblock)

        assigns = { scope:[] for scope in scopes }

        for scope in scopes:
            assigns[scope].extend(find_all(scope, test=lambda n: isinstance(n, Assign), stop=creates_new_variable_scope))

        print("all if assigns", list(assigns))

        declarations = { scope:{} for scope in scopes }

        for scope in scopes:
            for assign in assigns[scope]:
                if hasattr(assign, "already_declared"):
                    continue
                if isinstance(assign.lhs, Identifier) and not assign.lhs.declared_type and not assign.scope.find_def(assign.lhs):
                    if assign.lhs.name in declarations[scope]:
                        continue
                    declarations[scope][assign.lhs.name] = assign, codegen_node(assign.rhs, cx)
                else:
                    raise CodeGenError("unexpected non-simple assign in noscope if", assign)

        if all(declarations[scopes[0]].keys() == declarations[s].keys() for s in scopes[1:]):
            # allow noscope

            for lhs in declarations[scopes[0]]:
                assign, declname = declarations[scopes[0]][lhs]
                assign.already_declared = True
                cpp += f"decltype({declname}) {lhs};\n" + indt
            for scope in scopes[1:]:
                for lhs in declarations[scope]:
                    assign, declname = declarations[scope][lhs]
                    assign.already_declared = True
        else:
            raise CodeGenError("unbalanced assignments in if prevents noscope", ifnode)

    cpp += "if (" + codegen_node(ifnode.cond, cx) + ") {\n"

    cpp += codegen_block(ifnode.thenblock, cx.enter_scope())

    for elifcond, elifblock in ifnode.eliftuples:
        cpp += indt + "} else if (" + codegen_node(elifcond, cx.enter_scope()) + ") {\n"
        cpp += codegen_block(elifblock, cx.enter_scope())

    if ifnode.elseblock:
        cpp += indt + "} else {\n"
        cpp += codegen_block(ifnode.elseblock, cx.enter_scope())

    cpp += indt + "}"

    if is_expression:
        if cx.in_function_body:
            capture = "&"
        else:
            capture = ""
        cpp = "[" + capture + "]() {" + cpp + "}()"

    return cpp + "\n"


def codegen_for(node, cx):
    assert isinstance(node, Call)
    if len(node.args) != 2:
        raise CodeGenError("'for' must have two arguments - the iteration part and the indented block. 'One liner' for loops are not supported.", node)
    arg, block = node.args
    if not isinstance(block, Block):
        raise CodeGenError("expected block as last arg of for", node)
    type_str = None

    if not isinstance(arg, BinOp) and isinstance(arg, Identifier) and arg.declared_type is not None:
        # our low precedence choice for ':' - which works well for one liner ifs eg if (x and y: print(5))
        # - does not work so well for:
        # for (x: const:int in it:
        #     pass
        # )
        # still, the syntax above even if "parsed wrong" beats the alternatives (odd for loop syntax with type at the end or tightening precedence of : or loosening precedence of 'in'). so we'll just accept that typed-fors are represented oddly in the ast
        # (though maybe this should be done in an earlier pass like expanded if one-liners)
        itertypes = type_node_to_list_of_types(arg.declared_type)
        if not itertypes:
            raise CodeGenError("unexpected typed for-loop first arg (not enough elements", node)
        instmt = itertypes.pop()
        lasttype = instmt.lhs
        # we should really re-create or mutate here (wrong parent) but it's fine for now
        itertypes.append(lasttype)
        if not all(isinstance(i, Identifier) for i in itertypes):
            raise CodeGenError("unexpected non-Identifier type for for-loop iter var", node)

        arg.declared_type = None  # this sort of thing is unfortunate (TODO remove .declared_type)
        instmt.args[0] = arg
        # TODO we should rebuild a TypeOp instead of copying the logic of codegen_type
        first_type = codegen_type(arg, itertypes.pop(0), cx)
        type_str = first_type + " ".join(codegen_type(arg, t, cx, _is_leading=False) for t in itertypes)
    else:
        instmt = node.args[0]


    if not isinstance(instmt, BinOp) and instmt.func == "in": # fix non node args
        raise CodeGenError("unexpected 1st argument to for", node)

    var = instmt.lhs
    iterable = instmt.rhs

    if not isinstance(var, Identifier):
        # TODO for ((x,y):const:auto in pairs:
        raise CodeGenError("Unexpected iter var", var)

    # if the user took enough care to consult the precedence table followed by using parenthesese for their for loop variable...
    if var.declared_type is not None:
        assert type_str is None
        type_str = codegen_type(var, var.declared_type, cx)
        var_str = var.name
    else:
        var_str = codegen_node(var, cx)

    indt = cx.indent_str()

    # forstr = indt + 'for(const auto& {} : {}) {{\n'.format(codegen_node(var), codegen_node(iterable))

    # TODO: remove 'range' as a builtin entirely? (needs testsuite fixes) or maybe still keep simple for x in range(x, y) as a built-in macro (but remove printing of std.views.iota in other contexts?)
    if isinstance(iterable, Call) and iterable.func.name == "range":
        if not 0 <= len(iterable.args) <= 2:
            raise CodeGenError("unsupported range args", iterable)

        # use of types with range untested
        # if not isinstance(var, Identifier) or var.declared_type is not None or type_str is not None:
        #     raise CodeGenError("no complex iteration type declarations with 'range' builtin", var)

        start = iterable.args[0]
        if len(iterable.args) == 2:
            end = iterable.args[1]
        else:
            end = start
            start = IntegerLiteral(integer=0, source=None)
            start.parent = end.parent
        # sub = BinOp(func="-", args=[end, start], source=None)
        # sub.parent = start.parent
        # ds = decltype_str(sub, cx)
        # ds = "decltype(" + codegen_node(sub, cx) + ")"
        startstr = codegen_node(start, cx)
        if type_str is None:
            type_str = f"std::remove_cvref_t<decltype({startstr})>"
        endstr = codegen_node(end, cx)
        forstr = f"{indt}static_assert(std::is_same_v<std::remove_cvref_t<decltype({startstr})>, std::remove_cvref_t<decltype({endstr})>>);\n"
        forstr += f"{indt}for ({type_str} {var_str} = {startstr}; {var_str} < {endstr}; ++{var_str}) {{\n"
        #     start_str = codegen_node(start, cx)
        #     end_str = codegen_node(end, cx)
        #     preamble = "{\n"
        #     # constexpr = indt + "if constexpr (is_signed(" + start_str + ") {\n"
        #     # constexpr += indt + decltype_str(start) + ";\n"
        #     # constexpr += indt + "else {"
        #     # constexpr += indt + decltype_str(end_str) + ";\n"
        #     # constexpr +=  indt + f"for ({decliter} {i})"
        # else:
        #     end = start
        #     start = 0
        # itertype = "decltype("
        # forstr +=
    else:
        # if var.declared_type is not None:
        #     # TODO this is awkward
        #     typed_var_str = codegen_type(var, var.declared_type, cx)
        #     vartype = var.declared_type
        #     var.declared_type = None
        #     typed_var = typed_var_str + " " + codegen_node(var, cx)
        #     var.declared_type = vartype
        #
        #     # varnode =

        if type_str is None:
            type_str = "const auto&"

        forstr = indt + 'for({} {} : {}) {{\n'.format(type_str, var_str, codegen_node(iterable, cx))

    block_cx = cx.enter_scope()
    forstr += codegen_block(block, block_cx)
    forstr += indt + "}\n"
    return forstr


def is_comment(node):
    return isinstance(node, ScopeResolution) and node.lhs.name == "ceto" and (
            isinstance(node.rhs, Call) and node.rhs.func.name == "comment")


def is_super_init(call):
    return isinstance(call, Call) and isinstance(call.func,
        AttributeAccess) and call.func.lhs.name == "super" and call.func.rhs.name == "init"


def is_self_field_access(node):
    if isinstance(node, AttributeAccess) and node.lhs.name == "self":
        if not isinstance(node.rhs, Identifier):
            raise CodeGenError("unexpected attribute access", node)
        return True
    return False


def codegen_class(node : Call, cx):
    assert isinstance(node, Call)
    name = node.args[0]
    inherits = None

    if isinstance(name, Call):
        if len(name.args) != 1:
            if len(name.args) == 0:
                raise CodeGenError("empty inherits list", name)
            raise CodeGenError("Multiple inheritance is not supported (and we're leaning towards not ever using the 'inheritance list' for interface conformance etc either)", name)
        inherits = name.args[0]
        name = name.func

    if not isinstance(name, Identifier):
        raise CodeGenError("bad class first arg", name)
    block = node.args[-1]
    if not isinstance(block, Block):
        raise CodeGenError("class missing block (TODO forward declarations)", node)

    defined_interfaces = defaultdict(list)
    local_interfaces = set()
    typenames = []

    indt = cx.indent_str()
    inner_cx = cx.enter_scope()
    inner_cx.in_class_body = True
    inner_cx.in_function_body = False

    classdef = ClassDefinition(name, node, is_generic_param_index={},
                               is_unique=node.declared_type and node.declared_type.name == "unique")

    cx.class_definitions.append(classdef)

    cpp = indt
    inner_indt = inner_cx.indent_str()
    uninitialized_attributes = []
    uninitialized_attribute_declarations : typing.List[str] = []
    constructor_node = None
    constructor_initialized_field_names : typing.List[str] = []
    should_disable_default_constructor = False
    field_types : typing.Dict[str, typing.Union[str, Node]] = {}

    for block_index, b in enumerate(block.args):
        if isinstance(b, Call) and b.func.name == "def":
            methodname = b.args[0]

            if (method_type := b.args[0].declared_type) is not None:
                if isinstance(method_type, Call) and method_type.func.name == "interface" and len(method_type.args) == 1:
                    interface_type = method_type.args[0]
                    if methodname.name in ["init", "destruct"]:
                        raise CodeGenError("init or destruct can't defined as interface methods", b)

                    if interface_type.name in defined_interfaces or not any(t == interface_type.name for t in cx.interfaces):
                        defined_interfaces[interface_type.name].append(b)

                    cx.interfaces[interface_type.name].append(b)
                    local_interfaces.add(interface_type.name)

            if methodname.name == "init":
                if constructor_node is not None:
                    raise CodeGenError("Delegating constructors are not yet implemented (only one init method allowed for now)", b)
                constructor_node = b
            else:
                funcx = inner_cx.enter_scope()
                funcx.in_function_param_list = True
                cpp += codegen_def(b, funcx)
        elif isinstance(b, Identifier):

            if b.name == "pass":
                continue
            elif b.declared_type is None:  # or b.declared_type.name in ["mut", "const"]:  # BAD: don't make it easy/convenient to declare const data members
                # generic case
                t = gensym("C")
                typenames.append(t)
                field_types[b.name] = t
                decl_const_part = ""
                # BAD: don't promote const data members (remove this commented code)
                # if (b.declared_type is None and not mut_by_default) or (b.declared_type and b.declared_type.name == "const"):
                #     decl_const_part = "const "
                decl = decl_const_part + t + " " + b.name
                cpp += inner_indt + decl + ";\n\n"
                classdef.is_generic_param_index[block_index] = True
            else:
                # idea to "flatten out" the generic params is too crazy (and supporting the same behaviour in function defs means losing auto function arg deduction (more spamming decltype would maybe fix)
                # dependent_class = cx.lookup_class(b.declared_type)
                # if dependent_class is not None and dependent_class.num_generic_params > 0:
                #     # TODO fix unique here
                #     deps = [gensym("C") for _ in range(dependent_class.num_generic_params)]
                #     typenames.extend(deps)
                #     decl = "std::shared_ptr<" + dependent_class.name_node.name + "<" + ", ".join(deps) + ">> " + b.name
                # else:
                field_type = b.declared_type
                decl = codegen_type(b, b.declared_type, inner_cx) + " " + b.name
                field_types[b.name] = field_type
                # field_type_const_part, field_type_str = codegen_variable_declaration_type(b, cx)  # BAD / remove this: const data members are bad
                # decl = field_type_const_part + field_type_str + " " + b.name
                cpp += inner_indt + decl + ";\n\n"
                classdef.is_generic_param_index[block_index] = False

            uninitialized_attributes.append(b)
            uninitialized_attribute_declarations.append(decl)
        elif isinstance(b, Assign):
            cpp += inner_indt + codegen_assign(b, inner_cx) + ";\n\n"
        elif is_comment(b):
            cpp += codegen_node(b, inner_cx)
        else:
            raise CodeGenError("Unexpected expression in class body", b)

    base_class_type : typing.Optional[str] = inherits.name if inherits is not None else None
    classdef.is_concrete = not classdef.is_generic_param_index

    if constructor_node is not None:
        constructor_args = constructor_node.args[1:-1]
        constructor_block = constructor_node.args[-1]
        assert isinstance(constructor_block, Block)
        initializerlist_assignments = []
        super_init_call = None
        params_initializing_fields = []
        initcx = inner_cx.enter_scope()
        # initcx.in_function_param_list = True  # TODO remove this field

        for stmt in constructor_block.args:

            # handle self.whatever = something
            if isinstance(stmt, Assign) and is_self_field_access(stmt.lhs):
                field = stmt.lhs.rhs
                initializerlist_assignments.append((field, stmt.rhs))
                constructor_initialized_field_names.append(field.name)
                params_initializing_fields.extend(
                    (a, field.name) for a in constructor_args if
                    a.name == stmt.rhs.name)
            elif is_super_init(stmt):
                if super_init_call is not None:
                    raise CodeGenError("only one call to super.init allowed", stmt)
                super_init_call = stmt
            else:
                # anything that follows won't be printed as an initializer-list assignment/base-class-constructor-call
                break

        constructor_block.args = constructor_block.args[
                                 len(initializerlist_assignments) + int(super_init_call is not None):]

        if any(find_all(constructor_block, is_super_init)):
            raise CodeGenError("A call to super.init must occur in the 'initializer list' (that is, any statements before super.init must be of the form self.field = val")

        init_params = []
        init_param_type_from_name = {}

        for arg in constructor_args:
            if not isinstance(arg, Assign):
                should_disable_default_constructor = True

            if typed_arg_tuple := _codegen_typed_def_param_as_tuple(arg, initcx):
                typed_arg_str_lhs, typed_arg_str_rhs = typed_arg_tuple
                init_params.append(typed_arg_str_lhs + " " + typed_arg_str_rhs)
                if isinstance(arg, (Assign, NamedParameter)):
                    assert arg.lhs.name
                    init_param_type_from_name[arg.lhs.name] = typed_arg_str_lhs
                else:
                    assert isinstance(arg, Identifier)
                    init_param_type_from_name[arg.name] = typed_arg_str_lhs

            elif isinstance(arg, Identifier):
                # generic constructor arg:

                found_type = False
                for param, field_name in params_initializing_fields:
                    if arg is param and field_name in field_types:
                        field_type = field_types[field_name]
                        found_type = True
                        if isinstance(field_type, Node):
                            # mutate the ast so that we print arg with proper "lists/strings/objects const ref in func params" behavior
                            arg.declared_type = field_type
                            typed_arg_str_lhs, typed_arg_str_rhs = _codegen_typed_def_param_as_tuple(arg, initcx)  # this might add const& etc
                            init_params.append(typed_arg_str_lhs + " " + typed_arg_str_rhs)
                            init_param_type_from_name[arg.name] = typed_arg_str_lhs
                        else:
                            # generic field case
                            init_params.append("const " + field_type + "& " + arg.name)
                            init_param_type_from_name[arg.name] = field_type

                if not found_type:
                    t = gensym("C")
                    typenames.append(t)
                    init_params.append("const " + t + "& " + arg.name)
                    init_param_type_from_name[arg.name] = t
            else:
                raise CodeGenError("unexpected constructor arg", b)

        cpp += inner_indt + "explicit " + name.name + "(" + ", ".join(
            init_params) + ")"

        initializer_list_items = [
            codegen_node(field, initcx) + "(" + codegen_node(rhs, initcx) + ")"
            for field, rhs in initializerlist_assignments]

        if super_init_call is not None:
            if len(super_init_call.args) == 0:
                raise CodeGenError("no explicit calls to super.init() without args (just let c++ do this implicitly)")

            super_init_fake_args = []

            for arg in super_init_call.args:
                if isinstance(arg, Identifier) and arg.name in init_param_type_from_name:
                    # forward the type of the constructor arg to the base class constructor call
                    # TODO we could be smarter about not adding const ref to the types in the below map in the first place (that is make _codegen_typed_def_param_as_tuple return the non const ref unadorned type too)
                    super_init_fake_args.append("std::declval<std::remove_cvref_t<" + init_param_type_from_name[arg.name] +  ">>()")
                elif is_self_field_access(arg):  # this would fail in C++
                    raise CodeGenError("no reads from self in super.init call", arg)
                else:
                    # this is silly:
                    # super_init_fake_args.append("std::declval<std::remove_cvref_t<decltype(" + codegen_node(arg, inner_cx) + ")>>()")
                    super_init_fake_args.append(codegen_node(arg, inner_cx))

            super_init_args = [codegen_node(a, inner_cx) for a in super_init_call.args]

            inherits_dfn = cx.lookup_class(inherits)

            if not inherits_dfn.is_concrete and not inherits_dfn.is_pure_virtual:
                # here CTAD takes care of the real type of the base class (in case the base class is a template)
                # see https://stackoverflow.com/questions/74998572/calling-base-class-constructor-using-decltype-to-get-more-out-of-ctad-works-in
                base_class_type = "decltype(" + inherits.name + "(" + ", ".join(super_init_fake_args) + "))"
                # this is only necessary for msvc (see above link) but it's fine on other platforms:
                base_class_type = "std::type_identity_t<" + base_class_type + ">"

            super_init_str = base_class_type + " (" + ", ".join(super_init_args) + ")"
            initializer_list_items.insert(0, super_init_str)  # TODO we should preserve the user defined order

        initializer_list = ", ".join(initializer_list_items)

        if initializer_list:
            cpp += " : " + initializer_list + " "

        cpp += "{\n"
        cpp += codegen_function_body(constructor_node, constructor_block, initcx)
        cpp += inner_indt + "}\n\n"

    uninitialized_attributes = [u for u in uninitialized_attributes if u.name not in constructor_initialized_field_names]

    if uninitialized_attributes:
        if constructor_node is not None:
            raise CodeGenError("class {} defines a constructor (init method) but does not initialize these attributes: {}".format(name.name, ", ".join(str(u) for u in uninitialized_attributes)))

        # autosynthesize constructor
        cpp += inner_indt + "explicit " + name.name + "(" + ", ".join(uninitialized_attribute_declarations) + ") : "
        cpp += ", ".join([a.name + "(" + a.name + ")" for a in uninitialized_attributes]) + " {}\n\n"
        should_disable_default_constructor = True

    if should_disable_default_constructor:
        # this matches python behavior (though we allow a default constructor for a class with no uninitialized attributes and no user defined constructor)
        cpp += inner_indt + name.name + "() = delete;\n\n"

    interface_def_str = ""
    for interface_type in defined_interfaces:
        # note that shared_ptr<interface_type> is auto derefed
        interface_def_str += "struct " + interface_type + " : ceto::object {\n"
        for method in defined_interfaces[interface_type]:
            print("method",method)
            interface_def_str += inner_indt + interface_method_declaration_str(method, cx)
        interface_def_str += inner_indt + "virtual ~" + interface_type + "() = default;\n\n"
        interface_def_str +=  "};\n\n"

    cpp += indt + "};\n\n"

    default_inherits = ["public " + i for i in local_interfaces]
    if base_class_type is not None:
        default_inherits.append("public " + base_class_type)

    if not inherits:
        if classdef.is_unique:
            default_inherits += ["ceto::object"]
        else:
            default_inherits += ["ceto::shared_object"]

    class_header = "struct " + name.name + " : " + ", ".join(default_inherits)
    class_header += " {\n\n"

    if typenames:
        template_header = "template <" + ",".join(["typename " + t for t in typenames]) + ">"
    else:
        template_header = ""

    return interface_def_str + template_header + class_header + cpp


def codegen_while(whilecall, cx):
    assert isinstance(whilecall, Call)
    assert whilecall.func.name == "while"
    if len(whilecall.args) != 2:
        raise CodeGenError("Incorrect number of while args", whilecall)
    if not isinstance(whilecall.args[1], Block):
        raise CodeGenError("Last while arg must be a block", whilecall.args[1])

    cpp = "while (" + codegen_node(whilecall.args[0], cx.enter_scope()) + ") {"
    cpp += codegen_block(whilecall.args[1], cx.enter_scope())
    cpp += cx.indent_str() + "}\n"
    return cpp


def codegen_block(block: Block, cx):
    assert isinstance(block, Block)
    assert not isinstance(block, Module)  # handled elsewhere
    cpp = ""
    indent_str = cx.indent_str()

    for b in block.args:
        if isinstance(b, Identifier):
            if b.name == "pass":
                cpp += indent_str + "; // pass\n"
                continue

        if isinstance(b, Call):
            if b.func.name == "for":
                cpp += codegen_for(b, cx)
                continue
            elif b.func.name == "class":
                cpp += codegen_class(b, cx)
                continue
            elif b.func.name == "if":
                cpp += codegen_if(b, cx)
                continue
            elif b.func.name == "while":
                cpp += codegen_while(b, cx)
                continue

        if b.declared_type is not None:
            # typed declaration

            types = type_node_to_list_of_types(b.declared_type)
            if any(t.name in ["typedef", "using"] for t in types):
                # TODO more error checking here
                # we might just want to ban 'using' altogether (dangerous in combination with _ceto_ defined classes (not structs)
                declared_type = b.declared_type
                cpp += codegen_type(b, b.declared_type, cx)
                b.declared_type = None
                cpp += " " + codegen_node(b, cx) + ";\n"
                b.declared_type = declared_type
                continue

            field_type_const_part, field_type_str = codegen_variable_declaration_type(b, cx)
            decl = field_type_const_part + field_type_str + " " + b.name
            cpp += " " + decl + ";\n"

            continue

        cpp += indent_str + codegen_node(b, cx)
        if not is_comment(b):
            cpp += ";\n"

    return cpp


def interface_method_declaration_str(defnode: Call, cx):
    assert defnode.func.name == "def"
    name_node = defnode.args[0]
    name = name_node.name
    args = defnode.args[1:]
    block = args.pop()
    assert isinstance(block, Block)

    params = []
    return_type_node = defnode.declared_type

    if return_type_node is None:
        raise CodeGenError("must specify return type of interface method")
    return_type = codegen_type(defnode, return_type_node, cx)

    is_const = not mut_by_default

    specifier_node = name_node.declared_type

    type_nodes = type_node_to_list_of_types(specifier_node)

    const_or_mut = [t for t in type_nodes if t.name in ["const", "mut"]]
    if len(const_or_mut) > 1:
        raise CodeGenError("too many 'mut' and 'const' specified", defnode)

    if const_or_mut:
        if const_or_mut[0].name == "const":
            is_const = True
        elif const_or_mut[0].name == "mut":
            is_const = False

        type_nodes.remove(const_or_mut[0])

    const = " const" if is_const else ""
    specifier = ""

    type_nodes = [t for t in type_nodes if not (isinstance(t, Call) and t.func.name == "interface")]

    if type_nodes:
        specifier_node = list_to_typed_node(type_nodes)
        specifier = " " + codegen_type(name_node, specifier_node, cx) + " "

    for i, arg in enumerate(args):
        if arg.declared_type is None:
            raise CodeGenError("parameter types must be specified for interface methods")
        if not isinstance(arg, Identifier):
            raise CodeGenError("Only simple args allowed for interface method (you don't want c++ virtual functions with default arguments)")
        param = codegen_typed_def_param(arg, cx)
        assert len(param) > 0
        params.append(param)

    return "{}virtual {} {}({}){} = 0;\n\n".format(specifier, return_type, name, ", ".join(params), const)


def extract_mut_or_const(type_node : Node):
    if type_node is None:
        return None
    types = type_node_to_list_of_types(type_node)
    mc = list(t for t in types if t.name in ["mut", "const"])
    if len(mc) == 1:
        types.remove(mc[0])
        return mc[0], list_to_typed_node(types)
    return None


def strip_mut_or_const(type_node : Node):
    if mc := extract_mut_or_const(type_node):
        return mc[1]
    return type_node


def _should_add_const_ref_to_typed_param(param, cx):
    assert param.declared_type is not None
    type_node = strip_mut_or_const(param.declared_type)
    # note that mut:Foo (or Foo:mut), that is shared_ptr<Foo>, should still be passed by const ref
    if class_def := cx.lookup_class(type_node):
        return not class_def.is_unique
    return isinstance(param.declared_type, ListLiteral) or param.declared_type.name == "string" or isinstance(param.declared_type, (AttributeAccess, ScopeResolution)) and param.declared_type.lhs.name == "std" and param.declared_type.rhs.name == "string"


def codegen_typed_def_param(arg, cx):  # or default argument e.g. x=1
    t = _codegen_typed_def_param_as_tuple(arg, cx)
    if t:
        return " ".join(t)
    return None


def _strip_non_class_non_plain_mut_type(node : Node, cx):
    assert isinstance(node, Node)
    assert node.declared_type is not None
    types = type_node_to_list_of_types(node.declared_type)

    if len(types) <= 1:
        # don't strip 'mut' alone
        return None

    muts_only = [t for t in types if t.name == "mut"]

    num_muts = len(muts_only)
    if num_muts > 1:
        raise CodeGenError("too many 'mut' specifiers", node)

    if num_muts == 0:
        return None

    mut = muts_only[0]
    mut_index = types.index(mut)

    to_left_of_mut = None
    to_right_of_mut = None

    if mut_index > 0:
        to_left_of_mut = types[mut_index - 1]

    if mut_index < len(types) - 1:
        to_right_of_mut = types[mut_index + 1]

    if any(t for t in [to_left_of_mut, to_right_of_mut] if t and cx.lookup_class(t)):
        # don't strip 'mut' if adjacent to a class type
        return None

    types.remove(mut)
    return list_to_typed_node(types)


def _mutate_strip_non_class_non_plain_mut(node : Node, cx):
    assert isinstance(node, Node)
    assert node.declared_type is not None

    if stripped := _strip_non_class_non_plain_mut_type(node, cx):
        node.declared_type = stripped
        return True

    return False


def _codegen_typed_def_param_as_tuple(arg, cx):

    should_add_outer_const = not mut_by_default

    # TODO should handle plain 'mut'/'const' param (generic case)

    if arg.declared_type is not None:
        if isinstance(arg, Identifier):

            if _mutate_strip_non_class_non_plain_mut(arg, cx) or \
                    any(t.name == "const" for t in type_node_to_list_of_types(arg.declared_type)):  # TODO this needs to follow same logic as local vars (we're not adding add_const_t for a non-const pointer to const). ??? don't understand previous TODO but does this work with const:Foo meaning shared_ptr<const Foo> ? (seems to given that this logic previously incorrectly stripped 'mut' from mut:Foo)
                should_add_outer_const = False

            automatic_const_part = " "  # TODO add const here (if not already const)
            if should_add_outer_const:
                if (class_def := cx.lookup_class(arg.declared_type)) and class_def.is_unique:
                    # don't add const to unique managed param (it will impede automatic std::move from last use)
                    pass
                else:
                    automatic_const_part = "const "

            automatic_ref_part = ""

            if _should_add_const_ref_to_typed_param(arg, cx):
                automatic_const_part = "const "
                automatic_ref_part = "&"

            # treat e.g. external C++ types verbatim (except for adding 'const'
            type_part = automatic_const_part + codegen_type(arg, arg.declared_type, cx) + automatic_ref_part
            return type_part, " " + arg.name
        else:
            # params.append(autoconst(autoref(codegen_type(arg, arg.declared_type, cx))) + " " + codegen_node(arg, cx))
            # note precedence change making
            raise SemanticAnalysisError(
                "unexpected typed expr in defs parameter list", arg)
    elif isinstance(arg, Assign) and not isinstance(arg, NamedParameter):
        raise SemanticAnalysisError(
            "Overparenthesized assignments in def parameter lists are not treated as named params. To fix, remove the redundant parenthesese from:",
            arg)
    elif isinstance(arg, NamedParameter):
        if not isinstance(arg.lhs, Identifier):
            raise SemanticAnalysisError(
                "Non identifier left hand side in def arg", arg)

        if arg.lhs.declared_type is not None:

            if _mutate_strip_non_class_non_plain_mut(arg.lhs, cx) or \
                    any(t.name == "const" for t in type_node_to_list_of_types(arg.declared_type)):  # TODO this needs to follow same logic as local vars (we're not adding add_const_t for a non-const pointer to const). ??? don't understand previous TODO but does this work with const:Foo meaning shared_ptr<const Foo> ? (seems to given that this logic previously incorrectly stripped 'mut' from mut:Foo)
                should_add_outer_const = False

            automatic_const_part = " "
            automatic_ref_part = ""

            if _should_add_const_ref_to_typed_param(arg.lhs, cx):
                automatic_const_part = "const "
                automatic_ref_part = "&"

            if should_add_outer_const:

                if (class_def := cx.lookup_class(arg.lhs.declared_type)) and class_def.is_unique:
                    # don't add const to unique managed param (it will impede automatic std::move from last use)
                    pass
                else:
                    automatic_const_part = "const "

            type_part = automatic_const_part + codegen_type(arg.lhs, arg.lhs.declared_type, cx) + automatic_ref_part

            return type_part, arg.lhs.name + " = " + codegen_node(arg.rhs, cx)

        elif isinstance(arg.rhs, ListLiteral):
            if not arg.rhs.args:
                return "const std::vector<" + vector_decltype_str(arg, cx) + ">&", arg.lhs.name + " = {" + ", ".join( [codegen_node(a, cx) for a in arg.rhs.args]) + "}"
            else:
                # the above (our own poor reimplementation of CTAD with a bit of extra forward type inference) works but we can just use CTAD:

                # c++ gotcha - not usable as a default argument!
                # params.append("const auto& " + arg.lhs.name + " = std::vector {" + ", ".join(
                #         [codegen_node(a, cx) for a in arg.rhs.args]) + "}")

                # inferred part still relies on CTAD:
                vector_part = "std::vector {" + ", ".join(
                    [codegen_node(a, cx) for a in arg.rhs.args]) + "}"

                # but it's now usable as a default argument:
                return "const decltype(" + vector_part + ")& ", arg.lhs.name + " = " + vector_part
        # elif isinstance(arg.rhs, Call) and arg.rhs.func.name == "lambda":
        #     pass
        else:
            # note that this adds const& to lhs for known class constructor calls e.g. Foo() but note e.g. even if Foo() + 1 returns Foo, no automagic const& added
            if isinstance(arg.rhs, Call) and (class_def := cx.lookup_class(arg.rhs.func)):
                # it's a known class (object derived). auto add const&
                # (though std::add_const_t works here, we can be direct)
                make_shared = codegen_node(arg.rhs, cx)
                # (we can also be direct with the decltype addition as well though decltype_str works now)
                # TODO needs tests
                ref_part = ""
                if not class_def.is_unique:
                    ref_part = "&"
                return "const decltype(" + make_shared + ")" + ref_part, arg.lhs.name + " = " + make_shared
            else:
                # untyped default value

                automatic_const_part = ""
                automatic_ref_part = ""
                if isinstance(arg.rhs, (ListLiteral, StringLiteral)):
                    automatic_const_part = "const "
                    automatic_ref_part = "& "

                if should_add_outer_const:
                    automatic_const_part = "const "

                type_part = automatic_const_part + "decltype(" + codegen_node(arg.rhs, cx) + ")" + automatic_ref_part

                return type_part, arg.lhs.name + " = " + codegen_node(arg.rhs, cx)
        # else:
            #     raise SemanticAnalysisError(
            #         "Non identifier left hand side in def arg", arg)
            #     # params.append("const " + decltype_str(arg.rhs, cx) + "& " + codegen_node(arg.lhs, cx) + " = " + codegen_node(arg.rhs, cx))

    return None


def codegen_function_body(defnode : Call, block, cx):
    # methods or functions only (not lambdas!)
    assert defnode.func.name == "def"

    # Replace self.x = y in a method (but not an inner lambda!) with this->x = y
    need_self = False
    for s in find_all(defnode, test=lambda a: a.name == "self"):

        replace_self = True
        p = s
        while p is not defnode:
            if creates_new_variable_scope(p):
                # 'self.foo' inside e.g. a lambda body
                replace_self = False
                break
            p = p.parent

        if replace_self and isinstance(s.parent,
                                       AttributeAccess) and s.parent.lhs is s:
            # rewrite as this->foo:
            this = Identifier(name="this", source=None)
            arrow = ArrowOp(func="->", args=[this, s.parent.rhs], source=None)
            arrow.scope = s.scope
            this.scope = s.scope
            arrow.parent = s.parent.parent
            this.parent = arrow
            arrow.rhs.parent = arrow

            if s.parent in s.parent.parent.args:
                index = s.parent.parent.args.index(s.parent)
                s.parent.parent.args[index] = arrow
            elif s.parent is s.parent.parent.func:
                s.parent.parent.func = arrow
        else:
            need_self = True
    block_cx = cx.enter_scope()
    block_cx.in_function_body = True
    block_str = codegen_block(block, block_cx)
    if need_self:
        # (note: this will be a compile error in a non-member function / non-shared_from_this deriving class)
        block_str = block_cx.indent_str() + "const auto self = ceto::shared_from(this);\n" + block_str
    # if not is_destructor and not is_return(block.args[-1]):
    #     block_str += block_cx.indent_str() + "return {};\n"
    # no longer doing this^
    return block_str


def class_name_node_from_inline_method(defcallnode : Call):
    assert isinstance(defcallnode, Call)

    parentblock = defcallnode.parent
    if isinstance(parentblock, Assign):  # e.g. = 0 pure virtual function
        parentblock = parentblock.parent
    if isinstance(parentblock, Block) and isinstance(parentblock.parent, Call) and parentblock.parent.func.name == "class":
        classname = parentblock.parent.args[0]
        if isinstance(classname, Call):
            # inheritance
            classname = classname.func
        assert isinstance(classname, Identifier)
        return classname
    return None


def codegen_def(defnode: Call, cx):
    assert defnode.func.name == "def"
    name_node = defnode.args[0]
    name = name_node.name
    args = defnode.args[1:]
    if args and isinstance(args[-1], Block):
        block = args.pop()
        is_declaration = False
    else:
        block = None
        is_declaration = True

    return_type_node = defnode.declared_type

    if isinstance(name_node, Call) and name_node.func.name == "operator" and len(name_node.args) == 1 and isinstance(operator_name_node := name_node.args[0], StringLiteral):
        name = "operator" + operator_name_node.string

    if name is None:
        # no immediate plans to support out of line methods
        raise CodeGenError(f"can't handle name {name_node} in def {defnode}")

    params = []
    typenames = []

    # no support for out of line methods at the moment
    class_identifier = class_name_node_from_inline_method(defnode)
    is_method = class_identifier is not None
    if is_method:
        class_name = class_identifier.name
    else:
        class_name = None

    is_destructor = False
    if is_method and name == "destruct":
        if args:
            raise CodeGenError("destructors can't take arguments", defnode)
        is_destructor = True

    specifier_node = name_node.declared_type
    specifier_types = type_node_to_list_of_types(specifier_node)

    interface_calls = [t for t in specifier_types if isinstance(t, Call) and t.func.name == "interface"]
    if len(interface_calls) > 1:
        raise CodeGenError("too many 'interface' specifiers", defnode)
    elif len(interface_calls) == 1:
        interface = interface_calls[0]
        specifier_types.remove(interface)
    else:
        interface = None

    if interface and return_type_node is None:
        raise CodeGenError("must specify return type of interface method")
    assert is_method or not interface

    for i, arg in enumerate(args):
        if interface:
            if arg.declared_type is None:
                raise CodeGenError(
                    "parameter types must be specified for interface methods")
            if not isinstance(arg, Identifier):
                raise CodeGenError(
                    "Only simple args allowed for interface method (c++ virtual functions with default arguments are best avoided)")
        if typed_param := codegen_typed_def_param(arg, cx):
            params.append(typed_param)
        else:
            t = "T" + str(i + 1)
            # params.append(t + "&& " + arg.name)
            # params.append(t + " " + arg.name)
            params.append("const " + t + "& " + arg.name)
            typenames.append("typename " + t)

    template = ""
    inline = "inline "
    specifier = ""
    is_const = is_method and not mut_by_default

    if specifier_types:
        const_or_mut = [t for t in specifier_types if t.name in ["const", "mut"]]
        if len(const_or_mut) > 1:
            raise CodeGenError("too many 'mut' and 'const' specified", defnode)

        if const_or_mut:
            if not is_method:
                raise CodeGenError("Don't specify const/mut for a non-method", const_or_mut[0])
            is_const = const_or_mut[0].name == "const"
            specifier_types.remove(const_or_mut[0])

        if specifier_types:
            specifier_node = list_to_typed_node(specifier_types)
            specifier = " " + codegen_type(name_node, specifier_node, cx) + " "

            if any(t.name == "static" for t in specifier_types):
                if const_or_mut:
                    raise CodeGenError("const/mut makes no sense for a static function", const_or_mut[0])
                is_const = False

            def is_template_test(expr):
                return isinstance(expr, Template) and expr.func.name == "template"

            if list(find_all(specifier_node, test=is_template_test)):
                if len(typenames) > 0:
                    raise CodeGenError("Explicit template function with generic params", specifier_node)
                template = ""
            # inline = ""  # debatable whether a non-trailing return should inmply no "inline":
            # no: tvped func above a certain complexity threshold automatically placed in synthesized implementation file

    if interface:
        assert len(typenames) == 0
        template = ""
        inline = ""

    if is_declaration:
        inline = ""

    if typenames:
        template = "template <{0}>\n".format(", ".join(typenames))
        inline = ""

    if name == "main":
        if return_type_node or name_node.declared_type:
            raise CodeGenError("main implicitly returns int. no explicit return type or directives allowed.", defnode)
        template = ""
        inline = ""
        if not isinstance(defnode.parent, Module):
            raise CodeGenError("unexpected nested main function", defnode)
        defnode.parent.has_main_function = True

    if return_type_node:
        # return_type = codegen_type(name_node, name_node.declared_type)
        return_type = codegen_type(defnode, return_type_node, cx)
        if is_destructor:
            raise CodeGenError("destruct methods can't specifiy a return type")
    elif name == "main":
        return_type = "int"
    else:
        return_type = "auto"
        found_return = False
        if block:
            for b in block.args:
                for ret in find_all(b, test=is_return, stop=creates_new_variable_scope):
                    found_return = True
                    if is_void_return(ret):
                        # like python treat 'return' as 'return None' (we change the return type of the defined func to allow deduction of type of '{}' by c++ compiler)
                        # return_type = 'std::shared_ptr<object>'
                        # ^ this is buggy or at least confusing for all sorts of reasons e.g. classes managed by unique_ptr (we're now embracing void)
                        return_type = "void"
                        break

        if not found_return:
            # return_type = 'std::shared_ptr<object>'
            return_type = "void"

    if is_destructor:
        # TODO allow def (destruct:virtual:
        #                pass
        #            )
        # TODO: 'virtual' if class is 'inheritable' ('overridable'? 'nonfinal'?) (c++ class marked 'final' otherwise)
        # not marked virtual because inheritance not implemented yet (note that interface abcs have a virtual destructor)
        funcdef = "~" + class_name + "()"
    else:
        const = " const" if is_const else ""
        funcdef = "{}{}{}auto {}({}){} -> {}".format(template, specifier, inline, name, ", ".join(params), const, return_type)
        if interface:
            funcdef += " override" # maybe later: use final if method not 'overridable'

    indt = cx.indent_str()

    if is_declaration:
        if typenames:
            raise CodeGenError("no declarations with untyped/generic params", defnode)

        if not is_method and not isinstance(defnode.parent, Assign):
            raise CodeGenError("forward declarations not currently supported", defnode)

        rhs = defnode.parent.rhs

        if name == "init" and rhs.name in ["default", "delete"]:
            # return class_name + "() = " + defnode.parent.rhs.name
            raise CodeGenError("TODO decide best way to express = default/delete", defnode)

        if return_type_node is None:
            raise CodeGenError("declarations must specify a return type", defnode)

        if isinstance(rhs, IntegerLiteral) and rhs.integer == 0:

            classdef = cx.lookup_class(class_identifier)
            if not classdef:
                raise CodeGenError("expected a class in '= 0' declaration", class_identifier)

            classdef.is_pure_virtual = True

            # pure virtual function (codegen_assign handles the "= 0" part)
            return indt + funcdef
        else:
            raise CodeGenError("bad assignment to function declaration", defnode)

    block_str = codegen_function_body(defnode, block, cx)
    return indt + funcdef + " {\n" + block_str + indt + "}\n\n"


def codegen_lambda(node, cx):
    args = list(node.args)
    block = args.pop()
    assert isinstance(block, Block)
    # params = ["auto " + codegen_node(a) for a in args]
    params = []
    for a in args:
        if not isinstance(a, Identifier):
            if isinstance(a, Assign):
                raise CodeGenError("lambda args may not have default values (not supported in C++)", a)
            if isinstance(a, TypeOp):
                # lambda inside decltype on rhs of an outer type case (result of unfortunate choice in sema to not fully flatten TypeOp and only  partially convert to a .declared_type)
                realtype = a.rhs
                a = a.lhs
                a.declared_type = realtype
                if not isinstance(a, Identifier):
                    raise CodeGenError("Unexpected lambda argument for lambda found inside decltype", a)
            else:
                raise CodeGenError("Unexpected lambda argument", a)

        if typed_param := codegen_typed_def_param(a, cx):
            params.append(typed_param)
        else:
            params.append("const auto &" + a.name)
    newcx = cx.enter_scope()
    newcx.in_function_body = True
    type_str = ""
    invocation_str = ""
    if node.declared_type is not None:
        if isinstance(node.declared_type, (TypeOp, Call)):
            if isinstance(node.declared_type, Call):
                return_type_list = []
                last_type = node.declared_type
            elif isinstance(node.declared_type, TypeOp):
                return_type_list = type_node_to_list_of_types(node.declared_type)
                last_type = return_type_list.pop()

            if isinstance(last_type, Call):
                while isinstance(last_type.func, Call):#  and not last_type.func.func.name == "decltype":
                    invocation_str += "(" + ", ".join(codegen_node(a, cx) for a in last_type.args) + ")"
                    last_type = last_type.func

                if (isinstance(last_type.func, Identifier) and last_type.func.name != "decltype"):
                    # this is the case e.g. l = lambda(x:int, 0):int(0)
                    # decltype check avoids the case: l2 = lambda (x: int, 0):decltype(0)  # not an immediately invoked lambda
                    # but note that this is immediately invoked: l3 = lambda(x:int, 0):decltype(1)(2)
                    return_type_list.append(last_type.func)
                    invocation_str += "(" + ", ".join(codegen_node(a, cx) for a in last_type.args) + ")"
                elif isinstance(last_type, Call) and last_type.func.name == "decltype":
                    return_type_list.append(last_type)

                assert return_type_list
                declared_type = list_to_typed_node(return_type_list)
                node.declared_type = declared_type
                type_str = " -> " + codegen_type(node, declared_type, cx)

        if not type_str:
            type_str = " -> " + codegen_type(node, node.declared_type, cx)
    # if isinstance(node.func, ArrowOp):
    #     # not workable for precedence reasons
    #     if declared_type is not None:
    #         raise CodeGenError("Multiple return types specified for lambda?", node)
    #     declared_type = node.func.rhs
    #     # simplify AST (still messed with for 'is return type void?' stuff)
    #     node.declared_type = declared_type  # put type in normal position
    #     node.func = node.func.lhs  # func is now 'lambda' keyword

    if isinstance(node.func, ArrayAccess):
        # explicit capture list

        def codegen_capture_list_item(a):

            def codegen_capture_list_address_op(u : UnOp):
                if isinstance(u, UnOp) and u.func == "&" and isinstance(u.args[0], Identifier) and not u.args[0].declared_type:
                    # codegen would add parenthese to UnOp arg here:
                    return "&" + codegen_node(u.args[0], cx)
                return None

            if isinstance(a, Assign):
                if ref_capture := codegen_capture_list_address_op(a.lhs):
                    lhs = ref_capture
                elif isinstance(a.lhs, Identifier) and not a.lhs.declared_type:
                    lhs = codegen_node(a.lhs, cx)
                else:
                    raise CodeGenError("Unexpected lhs in capture list assign", a)
                return lhs + " = " + codegen_node(a.rhs, cx)
            else:
                if ref_capture := codegen_capture_list_address_op(a):
                    return ref_capture
                if isinstance(a, UnOp) and a.func == "*" and a.args[0].name == "this":
                    return "*" + codegen_node(a.args[0])
                if not isinstance(a, Identifier) or a.declared_type:
                    raise CodeGenError("Unexpected capture list item", a)
                if a.name == "ref":
                    # special case non-type usage of ref
                    return "&"
                elif a.name == "val":
                    return "="
                return codegen_node(a, cx)

        capture_list = [codegen_capture_list_item(a) for a in node.func.args]

    elif cx.parent.in_function_body:

        def is_capture(n):
            if not isinstance(n, Identifier):
                return False
            elif isinstance(n.parent, (Call, ArrayAccess, BracedCall, Template)) and n is n.parent.func:
                return False
            elif isinstance(n.parent, AttributeAccess) and n is n.parent.rhs:
                return False
            return True

        # find all identifiers but not call funcs etc or anything in a nested class
        idents = find_all(node, test=is_capture, stop=lambda c: isinstance(c.func, Identifier) and c.func.name == "class")

        idents = {i.name: i for i in idents}.values()  # remove duplicates

        possible_captures = []
        for i in idents:
            if i.name == "self":
                possible_captures.append(i.name)
            elif (d := i.scope.find_def(i)) and isinstance(d, (LocalVariableDefinition, ParameterDefinition)):
                defnode = d.defined_node
                is_capture = True
                while defnode is not None:
                    if defnode is node:
                        # defined in lambda or by lambda params (not a capture)
                        is_capture = False
                        break
                    defnode = defnode.parent
                if is_capture:
                    possible_captures.append(i.name)

        capture_list = [i + " = " + "ceto::default_capture(" + i + ")" for i in possible_captures]
    # elif TODO is nonescaping or immediately invoked:
    #    capture_list = "&"
    else:
        capture_list = ""
    # TODO:
    # lambda[ref](foo(x))
    # lambda[&x=x, y=bar(y)](foo(x,y))  # need to loosen ArrayAccess

    return ("[" + ", ".join(capture_list) + "](" + ", ".join(params) + ")" + type_str + " {\n" +
            codegen_block(block, newcx) + newcx.indent_str() + "}" + invocation_str)


def codegen(expr: Node):
    assert isinstance(expr, Module)
    cx = Scope()
    s = codegen_node(expr, cx)
    s = cpp_preamble + s
    print(s)
    return s


def decltype_str(node, cx):
    if isinstance(node, ArrayAccess):

        # for n, c in cx.find_defs(node.func): # doesn't work for forward inference (would require 2 passes - just keep using old find_defs for now)
        # for n, c in find_defs(node.func):
        for d in node.scope.find_defs(node.func):
            c = d.defining_node
            if isinstance(c, Assign):# and hasattr(c.rhs, "_element_decltype_str"):
                if vds := vector_decltype_str(c, cx):
                    return vds

        return "std::remove_cvref_t<{}>::value_type".format(decltype_str(node.func, cx))

    elif isinstance(node, ListLiteral):

        return "std::vector<" + decltype_str(node.args[0], cx) + ">"

    else:

        needs_outer_decltype, code = _decltype_str(node, cx)
        if needs_outer_decltype:
            code = "decltype(" + code + ")"
        return code


def _decltype_maybe_wrapped_in_declval(node, cx):
    needs_decltype, code = _decltype_str(node, cx)
    if not needs_decltype:
        return "std::declval<" + code + ">()"
    return code


def _decltype_str(node, cx):

    if isinstance(node, (IntegerLiteral, StringLiteral)):
        return True, codegen_node(node, cx)

    if isinstance(node, BinOp):
        binop = node
        if isinstance(node, AttributeAccess):
            # TODO needs fixes for implicit scope resolution
            return True, "ceto::mad(" + _decltype_maybe_wrapped_in_declval(node.lhs, cx) + ")->" + codegen_node(node.rhs, cx)

        return True, _decltype_maybe_wrapped_in_declval(binop.lhs, cx) + str(binop.func) + _decltype_maybe_wrapped_in_declval(binop.rhs, cx)

    elif isinstance(node, UnOp):
        assert False, "this needs fixes"
        return True, "(" + str(node.func) + _decltype_str(node.args[0], cx)[1] + ")"  # the other place unop is parenthesized is "necessary". here too?
    elif isinstance(node, Call) and isinstance(node.func, Identifier):
        call = node

        if class_def := cx.lookup_class(node.func):
            class_name = node.func.name
            class_node = class_def.class_def_node

            # if class_def.has_generic_params():
            #     class_name += "<" + ", ".join(
            #         [decltype_str(a, cx) for i, a in enumerate(node.args) if class_def.is_generic_param_index[i]]) + ">"

            # instead of manual tracking like the above,
            # leave the matter of the desired class type up to C++ CTAD:
            args_str = "(" + ", ".join([codegen_node(a, cx) for a in node.args]) + ")"   # this should be _decltype_str instead of codegen_node?

            const = "const " if _is_const_make(call) else ""

            class_name = "decltype(" + class_name + args_str + ")"

            if isinstance(class_node.declared_type,
                          Identifier) and class_node.declared_type.name == "unique":
                func_str = "std::unique_ptr<" + const + class_name + ">"
            else:
                func_str = "std::shared_ptr<" + const + class_name + ">"

            return False, func_str

        else:
            return True, codegen_node(call.func, cx) + "(" + ", ".join([_decltype_str(a, cx)[1] for a in call.args]) + ")"
    elif isinstance(node, ListLiteral):
        return True, "std::vector<" + decltype_str(node.args[0], cx) + "> {}"
    elif isinstance(node, ArrayAccess):

        # for n, c in cx.find_defs(node.func): # doesn't work for forward inference (would require 2 passes - just keep using old find_defs for now)
        # for n, c in find_defs(node.func):
        for d in node.scope.find_defs(node.func):
            c = d.defining_node
            if isinstance(c, Assign):# and hasattr(c.rhs, "_element_decltype_str"):
                if vds := vector_decltype_str(c, cx):
                    return False, vds
        return False, "std::remove_cvref_t<{}>::value_type".format(decltype_str(node.func, cx))

    assert isinstance(node, Identifier)

    # defs = list(find_defs(node))   # fails because only 1 (uncompleted) pass over ast to build scopes
    # defs = list(cx.find_defs(node))   # fails because only 1 (uncompleted) pass over ast to build scopes
    defs = list(node.scope.find_defs(node))
    if not defs:
        return True, node.name

    eligible_defs = list(defs)

    for d in defs:
        def_node, def_context = d.defined_node, d.defining_node

        if def_node.declared_type:

            if def_node.declared_type.name in ["mut", "const", "auto"]:
                # plain mut/const/auto provides no element type info
                continue
            elif isinstance(def_node.declared_type, TypeOp):

                type_list = type_node_to_list_of_types(def_node.declared_type)

                if any(t.name == "auto" for t in type_list):
                    # any use of auto also gives us no type info
                    continue
                elif "mut" in [type_list[0].name, type_list[-1].name]:
                    # discard east or west mut
                    if type_list[0].name == "mut":
                        type_list.pop(0)
                    else:
                        type_list.pop()
                    # there should be a real type left
                    rebuilt = list_to_typed_node(type_list)
                    return False, codegen_type(def_node, rebuilt, cx)
            else:
                return False, codegen_type(def_node, def_node.declared_type, cx)
        eligible_defs.append((def_node, def_context))

    if not eligible_defs:
        return True, node.name

    last_ident, last_context = eligible_defs[-1]

    if isinstance(last_context, Assign):
        assign = last_context

        return _decltype_str(assign.rhs, cx)

    elif isinstance(last_context, Call) and last_context.func.name == "for":
        instmt = last_context.args[0]
        if not isinstance(instmt, BinOp) and instmt.func == "in":
            raise CodeGenError("for loop should have in-statement as first argument ", last_context)
        if last_ident is instmt.lhs:  # maybe we should adjust find_defs to return the in-operator ?
            return True, "std::declval<typename std::remove_cvref_t<" + decltype_str(instmt.rhs, cx) + ">::value_type>()"

    else:
        return True, codegen_node(last_ident, cx)


def vector_decltype_str(node, cx):
    rhs_str = None
    assert isinstance(node, Assign)

    if isinstance(node, Assign) and isinstance(node.rhs, ListLiteral) and node.rhs.args:
        return decltype_str(node.rhs.args[0], cx)

    for found_use_node in find_uses(node):
        parent = found_use_node.parent
        while rhs_str is None and not isinstance(parent, Block):
            found_use_context = parent

            if isinstance(found_use_context, AttributeAccess) and (
               found_use_context.lhs is found_use_node and found_use_context.rhs.name == "append"):

                if isinstance(found_use_context.parent, Call) and len(found_use_context.parent.args) == 1:
                    append_arg = found_use_context.parent.args[0]
                    rhs_str = decltype_str(append_arg, cx)

            parent = parent.parent

        if rhs_str is not None:
            break
    return rhs_str


def _shared_ptr_str_for_type(type_node, cx):
    if not isinstance(type_node, Identifier):
        return None

    if classdef := cx.lookup_class(type_node):
        if isinstance(classdef, InterfaceDefinition):
            return "std::shared_ptr"

        class_node = classdef.class_def_node

        if isinstance(class_node.declared_type, Identifier) and class_node.declared_type.name == "unique":
            return "std::unique_ptr"
        else:
            return "std::shared_ptr"

    return None


def _codegen_extern_C(lhs, rhs):
    if isinstance(lhs, Identifier) and isinstance(rhs, StringLiteral) and lhs.name == "extern" and rhs.string == "C":
        return 'extern "C"'
    return None


def _codegen_compound_class_type(lhs, rhs, cx):
    # these should all create:
    # c = C() : const  # auto c = make_shared<const decltype(C())> ();
    # east/west:
    # c:const:C = C()  # const shared_ptr<const C> c = make_shared<const C)> ();
    # c:C:const = C()  # const shared_ptr<C const> c = make_shared<C const> ();

    # this would remain as is (c2 is just a const shared_ptr<C>)
    # s = C()
    # c2: const:auto = s  # if we continue to disallow just 'const'
    # c2: const = s  # even if we allow 'const' as a shorthand for 'auto:const' this could still be const shared_ptr<C>
    # c3: const = C()  # same
    # c4: const:C = s  # error can't convert shared_ptr<C> to shared_ptr<const C>
    # c5: const:C = s : const  # do we allow this as a convenient shorthand for static_pointer_cast?
    # c6: const:C = const(s)   # maybe this?

    for l, r in ((lhs,rhs), (rhs, lhs)):
        if c := cx.lookup_class(l):
            if not isinstance(r, Identifier) or r.name not in ["const", "mut", "weak"]:
                raise CodeGenError("Invalid specifier for class type")
            if r.name == "const":
                if c.is_unique:
                    return "std::unique_ptr<const " + l.name + ">"
                return "std::shared_ptr<const " + l.name + ">"
            elif r.name == "mut":
                if c.is_unique:
                    return "std::unique_ptr<" + l.name + ">"
                return "std::shared_ptr<" + l.name + ">"
            else:
                assert r.name == "weak"
                if c.is_unique:
                    raise CodeGenError("no weak specifier for unique-class", l)
                return "std::weak_ptr"


def codegen_type(expr_node, type_node, cx, _is_leading=True):

    if isinstance(expr_node, (ScopeResolution, AttributeAccess)) and type_node.name == "using":
        pass
    elif not isinstance(expr_node, (ListLiteral, Call, Identifier, TypeOp)):
        raise CodeGenError("unexpected typed expression", expr_node)
    if isinstance(expr_node, Call) and expr_node.func.name not in ["lambda", "def"]:
        raise CodeGenError("unexpected typed call", expr_node)

    if isinstance(type_node, TypeOp):
        lhs = type_node.lhs
        rhs = type_node.rhs
        if s := _codegen_extern_C(lhs, rhs):
            return s
        elif s := _codegen_compound_class_type(lhs, rhs, cx):
            return s
        return codegen_type(expr_node, lhs, cx, _is_leading=_is_leading) + " " + codegen_type(expr_node, rhs, cx, _is_leading=False)
    elif isinstance(type_node, ListLiteral):
        if len(type_node.args) != 1:
            raise CodeGenError("Array literal type must have a single argument (for the element type)", expr_node)
        return "std::vector<" + codegen_type(expr_node, type_node.args[0], cx) + ">"
    elif isinstance(type_node, Identifier):
        if type_node.declared_type is not None:
            # TODO removing the 'declared_type' property entirely in favour of unflattened TypeOp would solve various probs
            declared_type = type_node.declared_type

            if s := _codegen_extern_C(type_node, declared_type):
                return s
            elif s := _codegen_compound_class_type(type_node, declared_type, cx):
                return s

            type_node.declared_type = None
            output = codegen_type(expr_node, type_node, cx, _is_leading=_is_leading) + " " + codegen_type(expr_node, declared_type, cx, _is_leading=False)
            type_node.declared_type = declared_type

            return output

        if _is_leading and type_node.name in ["ptr", "ref", "rref"]:
            raise CodeGenError(f"Invalid untyped specifier. Use explicit 'auto:{type_node.name}':", type_node)

        if type_node.name == "ptr":
            return "*"
        elif type_node.name == "ref":
            return "&"
        elif type_node.name == "rref":
            return "&&"

        if type_node.name in ["new", "goto"]:
            raise CodeGenError("nice try", type_node)

        if type_node.name == "mut":
            raise CodeGenError("unexpected placement of 'mut'", expr_node)

    if not isinstance(type_node, (Identifier, TypeOp, Call, Template, AttributeAccess, ScopeResolution)):
        raise CodeGenError("unexpected type", type_node)

    return codegen_node(type_node, cx)


def codegen_attribute_access(node: AttributeAccess, cx: Scope):
    assert isinstance(node, AttributeAccess)

    if isinstance(node.lhs, Identifier) and cx.lookup_class(node.lhs):
        if node.rhs.name == "class":
            # one might need the raw class name Foo rather than shared_ptr<(const)Foo> without going through hacks like std.type_identity_t<Foo:mut>::element_type.
            # Note that Foo.class.static_member is not handled (resulting in a C++ error for such code) - good because Foo.static_member already works even for externally defined C++ classes
            return node.lhs.name

        # TODO there's a bug/misfeature where class names are registered as VariableDefs (there's a similar bug with function def names that 'does the right thing for the wrong reasons' w.r.t e.g. lambda capture - will eventually need fixing too)
        return node.lhs.name + "::" + codegen_node(node.rhs, cx)

    if isinstance(node.lhs, (Identifier, AttributeAccess)):
        # implicit scope resolution:

        # Here we implement for example: in A.b.c, if A doesn't lookup as a variable, print whole thing as scope resolution A::b::c. Note this makes e.g. accessing data members of globals defined in external C++ headers impossible (good!). TODO Such accesses can be allowed in the future once a python-style 'global' is implemented

        # e.g. std.q.r.s should print as std::q::r::s
        # HOWEVER std.q.r().s should print as std::q::r().s  where the last '.' is a maybe autoderef

        leading = node
        scope_resolution_list = []

        while isinstance(leading, AttributeAccess):
            scope_resolution_list.append(leading.rhs)
            leading = leading.lhs

        if isinstance(leading, Identifier) and leading.name != "self" and not leading.scope.find_def(leading):

            # I think we can get away without overparenthesizing chained scope resolutions (in C++ :: binds tightest so is not actually left associative - https://learn.microsoft.com/en-us/cpp/cpp/cpp-built-in-operators-precedence-and-associativity?view=msvc-170 is a better reference than https://en.cppreference.com/w/cpp/language/operator_precedence here)
            scope_resolution_code = leading.name
            while scope_resolution_list:
                if isinstance(scope_resolution_list[0], Identifier):
                    item = scope_resolution_list.pop()
                    scope_resolution_code += "::" + item.name
                else:
                    break

            if not scope_resolution_list:
                return scope_resolution_code
            else:
                remaining = list_to_attribute_access_node(scope_resolution_list)
                assert remaining is not None
                return scope_resolution_code + "::" + codegen_node(remaining, cx)

    # maybe autoderef
    return "ceto::mad(" + codegen_node(node.lhs, cx) + ")->" + codegen_node(node.rhs, cx)


def codegen_call(node: Call, cx: Scope):
    assert isinstance(node, Call)

    if is_call_lambda(node):
        newcx = cx.enter_scope()
        newcx.in_function_param_list = True
        return codegen_lambda(node, newcx)

    if isinstance(node.func, Identifier):
        func_name = node.func.name
        if func_name == "if":
            return codegen_if(node, cx)
        elif func_name == "def":
            return codegen_def(node, cx)
        elif func_name == "range":
            if len(node.args) == 1:
                return "std::views::iota(0, " + codegen_node(node.args[0],
                                                             cx) + ")"
                # return "std::ranges:iota_view(0, " + codegen_node(node.args[0], cx) + ")"
            elif len(node.args) == 2:
                return "std::views::iota(" + codegen_node(node.args[0],
                                                          cx) + ", " + codegen_node(
                    node.args[1], cx) + ")"
                # return "std::ranges:iota_view(" + codegen_node(node.args[0], cx) + ", " + codegen_node(node.args[1], cx) + ")"
            else:
                raise CodeGenError("range args not supported:", node)
        elif func_name == "operator" and len(node.args) == 1 and isinstance(
                operator_name_node := node.args[0], StringLiteral):
            return "operator" + operator_name_node.string
        else:
            arg_strs = [codegen_node(a, cx) for a in node.args]
            args_inner = ", ".join(arg_strs)
            args_str = "(" + args_inner + ")"

            if class_def := cx.lookup_class(node.func):
                class_name = node.func.name
                class_node = class_def.class_def_node
                curly_args = "{" + args_inner + "}"

                if not node.args:
                    # just use round parentheses to call default constructor
                    curly_args = args_str

                # if class_def.has_generic_params():
                #     class_name += "<" + ", ".join(
                #         [decltype_str(a, cx) for i, a in enumerate(node.args) if
                #          class_def.is_generic_param_index[i]]) + ">"
                class_name = "decltype(" + class_name + curly_args + ")"

                const_part = "const " if _is_const_make(node) else ""

                if isinstance(class_node.declared_type,
                              Identifier) and class_node.declared_type.name == "unique":
                    func_str = "std::make_unique<" + const_part + class_name + ">"
                else:
                    func_str = "std::make_shared<" + const_part + class_name + ">"

                return func_str + args_str

            if isinstance(node.func, Identifier):
                func_str = node.func.name
            else:
                func_str = codegen_node(node.func, cx)

            if cx.in_function_body:
                capture = "&"
            else:
                capture = ""

            simple_call_str = func_str + args_str

            if func_str in ("decltype", "static_assert") or (
                    isinstance(node.parent,
                               (ScopeResolution, ArrowOp, AttributeAccess)) and
                    node.parent.lhs is not node):
                if func_str == "decltype":
                    cx.in_decltype = True
                    if args_str.startswith("((") and args_str.endswith("))"):
                        # likely accidental overparenthesized decltype due to overenthusiastic parenthization in codegen
                        # strip the outside ones (fine for now)
                        # NOTE: this will break if the overparenthization in codegen is removed
                        return func_str + args_str[1:-1]
                return simple_call_str

            return simple_call_str

            # the below works in many cases but not with c++20 style vector CTAD. We'd have to go back to our py14 style diy vector CTAD to allow call_or_construct code in a vector e.g. ceto code of form l = [Foo(), Foo(), Foo()]

            dt_str = "decltype(" + simple_call_str + ")"

            simple_return = "return "
            if isinstance(node.parent, Block):
                simple_return = ""

            call_str = "[" + capture + "] { if constexpr (std::is_base_of_v<ceto::object, " + dt_str + ">) { return ceto::call_or_construct<" + dt_str + ">" + args_str + "; } else { " + simple_return + simple_call_str + "; } } ()"

            return call_str
    else:
        # probably a method:

        # not auto-flattening args is becoming annoying!
        # TODO make bin-op arg handling more ergonomic - maybe flatten bin-op args earlier (look at e.g. sympy's Add/Mul handling)
        method_name = None
        if isinstance(node.func, (AttributeAccess, ScopeResolution)):
            method_name = node.func.rhs
            while isinstance(method_name, (AttributeAccess, ScopeResolution)):
                method_name = method_name.rhs

        func_str = None

        if method_name is not None:

            # modify node.func (this is bad mutation and a source of future bugs)
            def consume_method_name():
                method_parent = method_name.parent
                assert method_parent.rhs is method_name

                if method_parent in method_parent.parent.args:
                    method_parent.parent.args.remove(method_parent)
                    method_parent.parent.args.append(method_parent.lhs)
                    method_parent.lhs.parent = method_parent.parent
                elif method_parent is method_parent.parent.func:
                    method_parent.parent.func = method_parent.lhs
                    method_parent.lhs.parent = method_parent.parent
                else:
                    assert 0

            if method_name.name == "operator" and len(
                    node.args) == 1 and isinstance(
                operator_name_node := node.args[0], StringLiteral):
                consume_method_name()
                return "ceto::mad(" + codegen_node(node.func, cx) + ")->operator" + operator_name_node.string

            elif method_name.parent and not isinstance(method_name.parent,
                                (ScopeResolution, ArrowOp)):
                # method_name.parent is None for a method call inside a decltype in a return type
                # TODO we maybe still have to handle cases where method_name.parent is None. silly example: x : decltype([].append(1)[0])

                consume_method_name()

                if method_name.name == "unsafe_at" and len(node.args) == 1:
                    return codegen_node(node.func, cx) + "[" + codegen_node(node.args[0], cx) + "]"

                if method_name.name == "append" and len(node.args) == 1:
                    # perhaps controversial rewriting of append to push_back
                    # this would also be the place to e.g. disable all unsafe std::vector methods (require a construct like (&my_vec)->data() to workaround while signaling unsafety)

                    # TODO replace this with a simple SFINAE ceto::append_or_push_back(arg) so we can .append correctly in fully generic code
                    append_str = "append"
                    is_list = False
                    if isinstance(node.func, ListLiteral):
                        is_list = True
                    else:
                        #for d in find_defs(node.func):
                        for d in node.scope.find_defs(node.func):
                            # print("found def", d, "when determining if an append is really a push_back")
                            if isinstance(d.defining_node, Assign) and isinstance(
                                    d.defining_node.rhs, ListLiteral):
                                is_list = True
                                break
                    if is_list:
                        append_str = "push_back"

                    func_str = "ceto::mad(" + codegen_node(node.func, cx) + ")->" + append_str
                else:

                    # TODO don't do the silly mutation above in the first place!
                    new_attr_access = AttributeAccess(func=".", args=[node.func, method_name], source=None)
                    func_str = codegen_attribute_access(new_attr_access, cx)

        if func_str is None:
            func_str = codegen_node(node.func, cx)

        return func_str + "(" + ", ".join(
            map(lambda a: codegen_node(a, cx), node.args)) + ")"


def _is_const_make(node):
    is_const = not mut_by_default

    if node.declared_type is not None:
        lhs_type = node.declared_type

        if isinstance(lhs_type, Identifier):
            if lhs_type.name == "mut":
                is_const = False
            elif lhs_type.name == "const":
                is_const = True
        elif isinstance(lhs_type, TypeOp):
            type_list = type_node_to_list_of_types(lhs_type)
            if "mut" in type_list:
                is_const = False
            elif "const" in type_list:
                is_const = True
    elif isinstance(node.parent,
                  Assign) and node.parent.lhs.declared_type is not None:
        lhs_type = node.parent.lhs.declared_type

        if isinstance(lhs_type, Identifier):
            if lhs_type.name == "mut":
                is_const = False
        elif isinstance(lhs_type, TypeOp):
            type_list = type_node_to_list_of_types(lhs_type)
            if "mut" in [type_list[0].name, type_list[-1].name]:
                is_const = False

    return is_const


def codegen_variable_declaration_type(node: Identifier, cx: Scope):
    if not isinstance(node, Identifier):
        raise CodeGenError("Unexpected typed expression", node)
    assert node.declared_type

    lhs_type_str = None

    const_specifier = ""

    if isinstance(node.declared_type, Identifier):
        # this should really be handled by codegen_assign
        if node.declared_type.name == "auto":
            # just "auto" means "const auto"
            # TODO this should take mut_by_default (or planned const/mut scopes) into account
            lhs_type_str = "const auto"
    elif isinstance(node.declared_type, TypeOp):
        type_list = type_node_to_list_of_types(node.declared_type)
        if "mut" in [type_list[0].name,
                     type_list[-1].name]:  # east or west mut is fine
            if type_list[0].name == "mut":
                type_list.pop(0)
            else:
                type_list.pop()
            rebuilt = list_to_typed_node(type_list)
            lhs_type_str = codegen_type(node, rebuilt, cx)
            assert len(lhs_type_str) > 0
        else:
            for i, t in enumerate(type_list):
                otheridx = i - 1 if i > 0 else i + 1
                if (t.name in ["const", "auto"] and type_list[otheridx].name in [
                    "const", "auto"]) or (
                        t.name == "const" and i < len(type_list) - 1 and type_list[
                    i + 1].name == "ref"):
                    # either contains "const auto", "auto const" or contains "const const"/"auto auto" (error in c++)
                    # alternately contains "const ref" anywhere
                    # use type verbatim
                    lhs_type_str = codegen_type(node, node.declared_type, cx)
                    break

            if lhs_type_str is None:
                if (type_list[0].name == "const" and type_list[
                    -1].name != "ptr") or type_list[-1].name == "const":
                    lhs_type_str = codegen_type(node, node.declared_type,
                                                cx)
                elif type_list[-1].name == "ptr":
                    lhs_type_str = codegen_type(node, node.declared_type,
                                                cx) + " const"

    if lhs_type_str is None:
        lhs_type_str = codegen_type(node, node.declared_type, cx)
        needs_const = not mut_by_default
        if needs_const and not const_specifier:
            const_specifier = "const "

    return const_specifier, lhs_type_str


def codegen_assign(node: Assign, cx: Scope):
    assert isinstance(node, Assign)

    if not isinstance(node.lhs, Identifier):
        return codegen_node(node.lhs, cx) + " = " + codegen_node(node.rhs, cx)

    is_lambda_rhs_with_return_type = False

    const_specifier = ""
    if not cx.in_function_body and not cx.in_class_body:
        # add constexpr to all global defns
        constexpr_specifier = "constexpr "
    else:
        constexpr_specifier = ""

    if node.declared_type is not None and isinstance(node.rhs,
                                                     Call) and node.rhs.func.name == "lambda":
        # TODO lambda return types need fixes? fixed now?
        lambdaliteral = node.rhs
        is_lambda_rhs_with_return_type = True
        # type of the assignment (of a lambda literal) is the type of the lambda not the lhs
        if lambdaliteral.declared_type is not None:
            raise CodeGenError("Two return types defined for lambda:",
                               node.rhs)
        lambdaliteral.declared_type = node.declared_type
        newcx = cx.enter_scope()
        newcx.in_function_param_list = True
        rhs_str = codegen_lambda(lambdaliteral, newcx)
    #elif node.lhs.declared_type is None and isinstance(node.rhs, ListLiteral) and not node.rhs.args and node.rhs.declared_type is None and (vds := vector_decltype_str(node, cx)) is not None:
    elif isinstance(node.rhs, ListLiteral) and not node.rhs.args and not node.rhs.declared_type and (not node.lhs.declared_type or not isinstance(node.lhs.declared_type, ListLiteral)) and (vds := vector_decltype_str(node, cx)) is not None:  # TODO const/mut specifier for list type on lhs
        # handle untyped empty list literal by searching for uses
        rhs_str = "std::vector<" + vds + ">()"
    else:
        rhs_str = codegen_node(node.rhs, cx)

    if isinstance(node.lhs, Identifier):
        lhs_str = node.lhs.name

        if node.lhs.declared_type:

            if node.lhs.declared_type.name in ["using", "namespace"]:
                return node.lhs.declared_type.name + " " + lhs_str + " = " + rhs_str

            # add const if not mut

            if isinstance(node.lhs.declared_type, Identifier) and node.lhs.declared_type.name in ["mut", "const"]:
                if cx.in_class_body:
                    # lhs_type_str = "std::remove_cvref_t<decltype(" + rhs_str + ")>"  # this would work but see error message
                    raise CodeGenError(f"const data members in C++ aren't very useful and prevent moves leading to unnecessary copying. Just use {node.lhs.name} = whatever (with no {node.lhs.declared_type.name} \"type\" specified)")
                else:
                    lhs_type_str = "const auto" if node.lhs.declared_type.name == "const" else "auto"
            else:
                if cx.in_class_body:
                    # don't call 'codegen_variable_declaration_type' which adds 'const' (TODO rethink previous refactors with codegen_assign called by codegen_class). See comments elsewhere re const data members in C++.
                    lhs_type_str = codegen_type(node.lhs, node.lhs.declared_type, cx)
                    const_specifier = ""
                else:
                    const_specifier, lhs_type_str = codegen_variable_declaration_type(node.lhs, cx)

            decl_str = lhs_type_str + " " + lhs_str

            const_specifier = constexpr_specifier + const_specifier

            plain_initialization = decl_str + " = " + rhs_str

            if isinstance(node.rhs, BracedLiteral):
                # aka "copy-list-initialization" in this case
                return const_specifier + plain_initialization

            # prefer brace initialization to disable narrowing conversions (in these assignments):

            direct_initialization = lhs_type_str + " " + lhs_str + " { " + rhs_str + " } "

            # ^ but there are still cases where this introduces 'unexpected' aggregate initialization
            # e.g. l2 : std.vector<std.vector<int>> = 1
            # should it be printed as std::vector<std::vector<int>> l2 {1} (fine: aggregate init) or std::vector<std::vector<int>> l2 = 1  (error) (same issue if e.g. '1' is replaced by a 1-D vector of int)
            # I think the latter behaviour for aggregates is less suprising: = {1} can be used if the aggregate init is desired.

            if node.lhs.declared_type.name == "mut" or any(t for t in type_node_to_list_of_types(node.lhs.declared_type) if t.name == "auto"):  # or _strip_non_class_non_plain_mut_type(node.lhs, cx):
                # no need to assert non-narrowing if lhs type codegen has 'auto'
                return const_specifier + direct_initialization

            # printing of UnOp is currently parenthesized due to FIXME current use of pyparsing infix_expr discards parenthesese in e.g. (&x)->foo()   (the precedence is correct but whether explicit non-redundant parenthesese are used is discarded)
            # this unfortunately can introduce unexpected use of overparenthesized decltype (this may be a prob in other places although note use of remove_cvref etc in 'list' type deduction.
            # FIXME: this is more of a problem in user code (see test changes). Also, current discarding of RedundantParens means user code can't explicitly call over-parenthesized decltype)
            # rhs_str = re.sub(r'^\((.*)\)$', r'\1', rhs_str)

            if isinstance(node.rhs, IntegerLiteral) or (
                    isinstance(node.rhs, Identifier) and node.rhs.name in [
                "true", "false"]):  # TODO float literals
                return f"{const_specifier}{direct_initialization}; static_assert(std::is_convertible_v<decltype({rhs_str}), decltype({node.lhs.name})>)"

            # So go given the above, define our own no-implicit-conversion init (without the gotcha for aggregates from naive use of brace initialization everywhere). Note that typed assignments in non-block / expression context will fail on the c++ side anyway so extra statements tacked on via semicolon is ok here.

            # note that 'plain_initialization' will handle cvref mismatch errors!
            return f"{const_specifier}{plain_initialization}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype({rhs_str}), std::remove_cvref_t<decltype({node.lhs.name})>>)"
    else:
        lhs_str = codegen_node(node.lhs, cx)

    assign_str = " ".join([lhs_str, node.func, rhs_str])

    # if not hasattr(node, "already_declared") and find_def(node.lhs) is None:
    # NOTE 'already_declared' is kludge only for 'noscope' ifs
    if not hasattr(node, "already_declared") and node.scope.find_def(node.lhs) is None:
        if cx.in_class_body:
            # "scary" may introduce ODR violation (it's fine plus plan for time being with imports/modules (in ceto sense) is for everything to be shoved into a single translation unit)
            # see https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2014/n3897.html
            assign_str = "std::remove_cvref_t<decltype(" + rhs_str + ")> " + lhs_str + " = " + rhs_str
        else:
            assign_str = "const auto " + assign_str

    const_specifier = constexpr_specifier + const_specifier

    return const_specifier + assign_str


def _is_unique_var(node: Identifier, cx: Scope):
    # should be handled in a prior typechecking pass (like most uses of find_defs)

    assert isinstance(node, Identifier)

    if not node.scope:
        # nodes on rhs of TypeOp currently don't have a scope
        return False

    for defn in node.scope.find_defs(node):
        if isinstance(defn, (LocalVariableDefinition, ParameterDefinition)):
            defining = defn.defining_node
            declared_type = strip_mut_or_const(defining.declared_type)
            classdef = cx.lookup_class(declared_type)
            if classdef and classdef.is_unique:
                return True
            elif isinstance(defining, Assign) and isinstance(rhs := strip_mut_or_const(defining.rhs), Call) \
                 and (classdef := cx.lookup_class(rhs.func)) and classdef.is_unique:
                return True

    return False


def codegen_node(node: Node, cx: Scope):
    assert isinstance(node, Node)

    if node.declared_type is not None:
        if not isinstance(node, (ListLiteral, Call)):
            if not isinstance(node, Identifier):
                raise CodeGenError("unexpected typed construct", node)

            if not isinstance(node.parent, Template):
                made_easy_lambda_args_mistake = False
                parent = node.parent
                while parent:
                    if isinstance(parent, Call):
                        if parent.func.name == "lambda":
                            made_easy_lambda_args_mistake = True
                            break
                        elif parent.func.name in ["def", "class"]:
                            made_easy_lambda_args_mistake = False
                            break
                    elif isinstance(parent, Block) and len(parent.args) != 1:
                        made_easy_lambda_args_mistake = False
                        break
                    parent = parent.parent
                if made_easy_lambda_args_mistake:
                    raise CodeGenError("do you have the args wrong? [ it's lambda(x, 5) not lambda(x: 5) ] in ", parent)

                raise CodeGenError("unexpected context for typed construct", node)

            return codegen_type(node, node, cx)  # this is a type inside a more complicated expression e.g. std.is_same_v<Foo, int:ptr>
        elif isinstance(node, Call) and node.func.name not in ["lambda", "def"] and node.declared_type.name not in ["const", "mut"]:
            raise CodeGenError("Unexpected typed call", node)

    if isinstance(node, Module):
        modcpp = ""
        for modarg in node.args:
            if isinstance(modarg, Call):
                if modarg.func.name == "def":
                    funcx = cx.enter_scope()
                    funcx.in_function_param_list = True
                    defcode = codegen_def(modarg, funcx)
                    modcpp += defcode
                    continue
                elif modarg.func.name == "class":
                    classcode = codegen_class(modarg, cx)
                    modcpp += classcode
                    continue
            modcpp += codegen_node(modarg, cx) + ";\n"  # untested # TODO: pass at global scope
        return modcpp
    elif isinstance(node, Call):
        return codegen_call(node, cx)

    elif isinstance(node, IntegerLiteral):
        return str(node)
    elif isinstance(node, Identifier):
        name = node.name

        if name == "ptr":
            raise CodeGenError("Use of 'ptr' outside type context is an error", node)
        elif name == "ref":
            raise CodeGenError("Use of 'ref' outside type context is an error", node)
        elif name == "None":
            return "nullptr"
        elif name == "dotdotdot":
            return "..."
        elif name == "string" and not isinstance(node.parent, (AttributeAccess, ScopeResolution)):
            return "std::string"
        # elif name == "object":
        #     return "std::shared_ptr<object>"

        if not (isinstance(node.parent, (AttributeAccess, ScopeResolution)) and
                node is node.parent.lhs) and (
           ptr_name := _shared_ptr_str_for_type(node, cx)):
            return ptr_name + "<" + ("const " if not mut_by_default else "") + name + ">"

        ident_ancestor = node.parent
        prev_ancestor = node
        is_last_use = True
        if isinstance(node.parent, (ScopeResolution, AttributeAccess, ArrowOp, Template)):
            is_last_use = False
        elif isinstance(node.parent, (BinOp, UnOp)):
            is_last_use = isinstance(node.parent, Assign)  # maybe a bit strict but e.g. we don't want to transform &x to &(std::move(x))
        elif isinstance(node.parent, Call) and node.parent.func is node:
            is_last_use = False

        while is_last_use and ident_ancestor and not creates_new_variable_scope(ident_ancestor):
            if isinstance(ident_ancestor, Block) and prev_ancestor in ident_ancestor.args:
                # TODO 'find_uses' in sema should work with Identifier not just Assign too
                # try:
                for b in ident_ancestor.args[ident_ancestor.args.index(prev_ancestor):]:
                    if any(find_all(b, lambda n: (n is not node) and (n.name == name))):
                        is_last_use = False
                        break
                # except ValueError:
                #     pass
            if any(n and n is not node and isinstance (n, Node) and name == n.name for n in ident_ancestor.args + [ident_ancestor.func]):
                is_last_use = False
                break
            prev_ancestor = ident_ancestor
            ident_ancestor = ident_ancestor.parent

        if is_last_use and _is_unique_var(node, cx):
            return "std::move(" + name + ")"

        return name

    elif isinstance(node, BinOp):

        if 0 and isinstance(node, NamedParameter):
            raise SemanticAnalysisError("Unparenthesized assignment treated like named parameter in this context (you need '(' and ')'):", node)

        elif isinstance(node, TypeOp):
            if isinstance(node, SyntaxTypeOp):
                if node.lhs.name == "return":
                    ret_body = codegen_node(node.rhs, cx)
                    if hasattr(node, "synthetic_lambda_return_lambda"):
                        lambdanode = node.synthetic_lambda_return_lambda
                        assert lambdanode
                        if lambdanode.declared_type is not None:
                            if lambdanode.declared_type.name == "void":
                                # the below code works but let's avoid needless "is_void_v<void>" checks
                                return ret_body

                            declared_type_constexpr = "&& !std::is_void_v<" + codegen_type(lambdanode, lambdanode.declared_type, cx) + ">"
                        else:
                            declared_type_constexpr = ""
                        # return if not void (void cast to suppress unused value warning - [[maybe_unused]] doesn't apply to (void) expressions)
                        return "if constexpr (!std::is_void_v<decltype(" + ret_body + ")>" + declared_type_constexpr + ") { return " + ret_body + "; } else { static_cast<void>(" + ret_body + "); }"
                    else:
                        return "return " + ret_body
                else:
                    assert False
            else:
                # dealing with subtype in a compound "type" (we're considering e.g. explict function template params as just complicated "return" types)
                # (consequence of not creating a .declared_type property for nested subtypes)

                # same handling as above case for nested expression with .declared_type

                # codegen_type should be handling compound types safely (any error checking for TypeOp lhs rhs should go there)
                return codegen_type(node, node, cx)

        elif isinstance(node, Assign):
            return codegen_assign(node, cx)

        else:
            if isinstance(node, AttributeAccess):
                return codegen_attribute_access(node, cx)

            elif is_comment(node):
                # probably needs to go near method handling logic now that precedence issue fixed (TODO re-enable comment stashing)
                if not (len(node.rhs.args) == 1 or isinstance(node.rhs.args[0], StringLiteral)):
                    raise CodeGenError("unexpected ceto::comment ", node)
                return "//" + node.rhs.args[0].func.replace("\n", "\\n") + "\n"

            funcstr = node.func  # fix ast: should be Ident
            if node.func == "and":  # don't use the weird C operators tho tempting
                funcstr = "&&"
            elif node.func == "or":
                funcstr = "||"

            binop_str = " ".join([codegen_node(node.lhs, cx), funcstr, codegen_node(node.rhs, cx)])

            if isinstance(node.parent, (BinOp, UnOp)) and not isinstance(node.parent, (ScopeResolution, ArrowOp, AttributeAccess)):
                # guard against precedence mismatch (e.g. extra parenthesese
                # not strictly preserved in the ast)
                # untested / maybe-buggy
                binop_str = "(" + binop_str + ")"

            return binop_str

    elif isinstance(node, ListLiteral):
        list_type = node.declared_type

        if list_type is None and isinstance(node.parent, Assign) and (list_assign_type := node.parent.lhs.declared_type):
            list_assign_type = strip_mut_or_const(list_assign_type)

            if isinstance(list_assign_type, ListLiteral):
                if not len(list_assign_type.args) == 1:
                    raise CodeGenError("unexpected args in list-type", list_assign_type)
                list_type = list_assign_type.args[0]

        elements = [codegen_node(e, cx) for e in node.args]

        if list_type is not None:
            return "std::vector<{}>{{{}}}".format(codegen_type(node, list_type, cx), ", ".join(elements))
        elif elements:
            # note: [[[1,2,3,4]]] should be a vector with 1 element not 4!

            if len(elements) > 1 or isinstance(node.args[0], ListLiteral):
                return "std::vector {{" + ", ".join(elements) + "}}"
            else:
                return "std::vector {" + ", ".join(elements) + "}"

            # no longer necessary CTAD reimplementation:
            # return "std::vector<{}>{{{}}}".format(decltype_str(node.args[0], cx), ", ".join(elements))
        else:
            raise CodeGenError("Cannot create vector without elements")
    elif isinstance(node, BracedLiteral):
        if isinstance(node.parent, Block):
            raise CodeGenError("Curly brace expression is invalid here. Use 'scope' for an anonymous scope.", node)
        elements = [codegen_node(e, cx) for e in node.args]
        return "{" + ", ".join(elements) + "}"
    elif isinstance(node, ArrayAccess):
        if len(node.args) > 1:
            raise CodeGenError("advanced slicing not supported yet")
        func_str = codegen_node(node.func, cx)
        idx_str = codegen_node(node.args[0], cx)
        return "ceto::maybe_bounds_check_access(" + func_str + "," + idx_str + ")"
    elif isinstance(node, BracedCall):
        if cx.lookup_class(node.func):
            # cut down on multiple syntaxes for same thing (even though the make_shared/unique call utilizes curly braces)
            raise CodeGenError("Use round parentheses for class constructor call", node)
        return codegen_node(node.func, cx) + "{" + ", ".join(codegen_node(a, cx) for a in node.args) + "}"
    elif isinstance(node, UnOp):
        opername = node.func
        if opername == ":":
            assert 0
        elif opername == "not":
            return "!" + codegen_node(node.args[0], cx)
        else:
            return "(" + opername + codegen_node(node.args[0], cx) + ")"
            # return opername + codegen_node(node.args[0], cx)
    elif isinstance(node, LeftAssociativeUnOp):
        opername = node.func
        return codegen_node(node.args[0], cx) + opername
    elif isinstance(node, StringLiteral):
        if isinstance(node.parent, Call) and node.parent.func.name in cstdlib_functions:
            return node.escaped()  # const char * !  TODO: stop doing this (fix testsuite)
        ffixes = [f.name for f in [node.prefix, node.suffix] if f]
        if "c" in ffixes and "s" in ffixes:
            raise CodeGenError("string literal cannot be both c-string and std::string", node)
        if node.prefix and node.prefix.name == "cpp":
            if node.suffix:
                raise CodeGenError("no suffixes for cpp-string", node)
            # unsafe embedded c++
            return node.string
        if "c" in ffixes or "s" in ffixes:
            if node.prefix and node.prefix.name in ["c", "s"]:
                str_prefix = node.prefix
                node.prefix = None
                code = str(node)
                node.prefix = str_prefix
                if node.prefix.name == "s":
                    return "std::string {" + code + "}"
                else:
                    return code
            elif node.suffix and node.suffix.name in ["c", "s"]:
                str_suffix = node.suffix
                node.suffix = None
                code = str(node)
                node.suffix = str_suffix
                if node.suffix.name == "s":
                    return "std::string {" + code + "}"
                else:
                    return code
        return "std::string {" + str(node) + "}"
    # elif isinstance(node, RedundantParens):  # too complicated letting codegen deal with this. just disable -Wparens
    #     return "(" + codegen_node(node.args[0]) + ")"
    elif isinstance(node, Template):
        # allow auto shared_ptr etc with parameterized classes e.g. f : Foo<int> results in shared_ptr<Foo<int>> f not shared_ptr<Foo><int>(f)
        # (^ this is a bit of a dubious feature when e.g. f: decltype(Foo(1)) works without this special case logic)
        template_args = "<" + ",".join([codegen_node(a, cx) for a in node.args]) + ">"
        if ptr_name := _shared_ptr_str_for_type(node.func, cx):
            return ptr_name + "<" + ("const " if not mut_by_default else "") + node.func.name + template_args + ">"
        else:
            return codegen_node(node.func, cx) + template_args

    assert False, "unhandled node"
