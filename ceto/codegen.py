import typing
from typing import Union, Any

from semanticanalysis import Node, Module, Call, Block, UnOp, BinOp, \
    TypeOp, Assign, NamedParameter, Identifier, IntegerLiteral, IfWrapper, \
    SemanticAnalysisError, SyntaxTypeOp, find_def, find_use, find_uses, \
    find_all, find_defs, is_return, is_void_return, RebuiltCall, RebuiltIdentifer
from parser import ListLiteral, TupleLiteral, BracedLiteral, ArrayAccess, \
    BracedCall, StringLiteral, AttributeAccess, RebuiltStringLiteral, \
    CStringLiteral, RebuiltBinOp, RebuiltInteger, Template, ArrowOp, \
    ScopeResolution, LeftAssociativeUnOp

from collections import defaultdict
import re


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
#include <stdexcept>

//#include <concepts>
//#include <ranges>
//#include <numeric>


#include "ceto.h"

"""


# Uses code and ideas from https://github.com/lukasmartinelli/py14


class ClassDefinition:

    def __init__(self, name_node : Identifier, class_def_node: Call, is_generic_param_index, is_unique):
        self.name_node = name_node
        self.class_def_node = class_def_node
        self.is_generic_param_index = is_generic_param_index
        self.is_unique = is_unique

    def has_generic_params(self):
        return True in self.is_generic_param_index.values()


class InterfaceDefinition(ClassDefinition):
    def __init__(self):
        pass

class Scope:

    def __init__(self):
        self.interfaces = defaultdict(list)
        self.class_definitions = []
        self.indent = 0
        self.parent : Scope = None
        self.in_function_body = False
        self.in_function_param_list = False
        self.in_class_body = False
        self.in_decltype = False

    def indent_str(self):
        return "    " * self.indent

    def lookup_class(self, class_node) -> typing.Optional[ClassDefinition]:
        if not isinstance(class_node, Identifier):
            return None
        for c in self.class_definitions:
            if isinstance(c.name_node, Identifier) and c.name_node.name == class_node.name:
                return c
        if class_node.name in self.interfaces:
            return InterfaceDefinition()
        if self.parent:
            return self.parent.lookup_class(class_node)
        return None

    def enter_scope(self):
        s = Scope()
        s.interfaces = self.interfaces.copy()
        self.class_definitions = list(self.class_definitions)
        s.parent = self
        s.in_function_body = self.in_function_body
        s.in_decltype = self.in_decltype
        s.indent = self.indent + 1
        return s


# method_declarations = []
cstdlib_functions = ["printf", "fprintf", "fopen", "fclose"]
counter = 0

def gensym(prefix=None):
    global counter
    counter += 1
    pre = "_langsym_"
    if prefix is not None:
        pre += prefix
    return pre + str(counter)


def creates_new_variable_scope(e: Node) -> bool:
    return isinstance(e, Call) and e.func.name in ["def", "lambda", "class", "struct"]


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
                synthetic_return = SyntaxTypeOp(func=":", args=[RebuiltIdentifer("return"), last_statement])
                last_statement.parent = synthetic_return
                a.args = a.args[0:-1] + [synthetic_return]

    ifnode = IfWrapper(ifcall.func, ifcall.args)

    if ifkind is not None and ifkind.name == "noscope":
        if is_expression or not cx.in_function_body:
            raise CodeGenError("unscoped if disallowed in expression context", ifcall)

        scopes = [ifnode.cond, ifnode.thenblock]
        if ifnode.elseblock is not None:
            scopes.append(ifnode.elseblock)
        for elifcond, elifblock in ifnode.eliftuples:
            scopes.append(elifcond)
            scopes.append(elifblock)

        assigns = []

        for scope in scopes:
            # assigns.extend(find_all(scope, test=lambda n: (isinstance(n, Assign) and not (isinstance(n.parent, Call) and n.parent.func.name == 'if')), stop=stop))
            assigns.extend(find_all(scope, test=lambda n: isinstance(n, Assign), stop=creates_new_variable_scope))

        print("all if assigns", list(assigns))

        declarations = {}

        for assign in assigns:
            if hasattr(assign, "already_declared"):
                continue
            if isinstance(assign.lhs, Identifier) and not find_def(assign.lhs):
                assign.already_declared = True
                if assign.lhs.name in declarations:
                    continue
                declarations[str(assign.lhs)] = codegen_node(assign.rhs, cx)

        for lhs in declarations:
            cpp += f"decltype({declarations[lhs]}) {lhs};\n" + indt

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

    return cpp


def codegen_for(node, cx):
    assert isinstance(node, Call)
    if len(node.args) != 2:
        raise CodeGenError("'for' must have two arguments - the iteration part and the indented block. 'One liner' for loops are not supported.", node)
    instmt = node.args[0]
    block = node.args[1]
    if not isinstance(block, Block):
        raise CodeGenError("expected block as last arg of for", node)
    if not isinstance(instmt, BinOp) and instmt.func == "in": # fix non node args
        raise CodeGenError("unexpected 1st argument to for", node)
    var = instmt.lhs
    iterable = instmt.rhs
    indt = cx.indent_str()
    # forstr = indt + 'for(const auto& {} : {}) {{\n'.format(codegen_node(var), codegen_node(iterable))
    var_str = codegen_node(var, cx)

    # TODO: remove 'range' as a builtin entirely (needs testsuite fixes)
    if isinstance(iterable, Call) and iterable.func.name == "range":
        if not 0 <= len(iterable.args) <= 2:
            raise CodeGenError("unsupported range args", iterable)

        start = iterable.args[0]
        if len(iterable.args) == 2:
            end = iterable.args[1]
        else:
            end = start
            start = RebuiltInteger(integer=0)
            start.parent = end.parent
        sub = RebuiltBinOp(func="-", args=[end, start])
        sub.parent = start.parent
        ds = decltype_str(sub, cx)
        startstr = codegen_node(start, cx)
        endstr = codegen_node(end, cx)
        forstr = f"for ({ds} {var_str} = {startstr}; {var_str} < {endstr}; ++{var_str}) {{\n"
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
        forstr = indt + 'for(auto && {} : {}) {{\n'.format(codegen_node(var, cx), codegen_node(iterable, cx))

    forstr += codegen_block(block, cx.enter_scope())
    forstr += indt + "}\n"
    return forstr


def is_comment(node):
    return isinstance(node, ScopeResolution) and node.lhs.name == "ceto" and (
            isinstance(node.rhs, Call) and node.rhs.func.name == "comment")


def codegen_class(node : Call, cx):
    assert isinstance(node, Call)
    name = node.args[0]
    assert isinstance(name, Identifier)
    block = node.args[-1]
    assert isinstance(block, Block)

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
    cpp += "int x;\n\n"
    inner_indt = inner_cx.indent_str()
    uninitialized_attributes = []
    uninitialized_attribute_declarations : typing.List[str] = []

    for block_index, b in enumerate(block.args):
        if isinstance(b, Call) and b.func.name == "def":
            methodname = b.args[0]

            interface_type = None

            if (method_type := b.args[0].declared_type) is not None:
                if isinstance(method_type, Call) and method_type.func.name == "interface" and len(method_type.args) == 1:
                    interface_type = method_type.args[0]
                    if methodname.name in ["init", "destruct"]:
                        raise CodeGenError("init or destruct cannot be defined as interface methods", b)

                    if interface_type.name in defined_interfaces or not any(t == interface_type.name for t in cx.interfaces):
                        defined_interfaces[interface_type.name].append(b)

                    cx.interfaces[interface_type.name].append(b)
                    local_interfaces.add(interface_type.name)
                else:
                    # def method_type_visitor(type_node):
                    #     if type_node.name in ["static", "const"]:
                    #         return type_node
                    #
                    # type_inorder_traversal(method_type, method_type_visitor)

                    # TODO const method signatures
                    pass # let codegen_def handle (works for 'static')

            if methodname.name == "init":
                constructor_args = b.args[1:-1]
                constructor_block = b.args[-1]
                assert isinstance(constructor_block, Block)
                initializerlist_assignments = []
                for stmt in constructor_block.args:

                    # handle self.whatever = something
                    if isinstance(stmt, Assign) and isinstance(stmt.lhs, AttributeAccess) and stmt.lhs.lhs.name == "self":
                        initializerlist_assignments.append(stmt)
                    else:
                        # anything that follows won't be printed as an initializer-list assignment
                        break
                constructor_block.args = constructor_block.args[len(initializerlist_assignments):]

                # for assign in initializerlist_assignments:

                # cpp += inner_indt + "explicit " + name.name + "("

                for arg in constructor_args:
                    if isinstance(arg, Identifier):
                        pass
                    elif isinstance(arg, NamedParameter):
                        pass
                    else:
                        raise CodeGenError("unexpected constructor arg", b)

            else:
                funcx = inner_cx.enter_scope()
                funcx.in_function_param_list = True
                cpp += codegen_def(b, funcx)
        elif isinstance(b, Identifier):
            if b.declared_type is not None:
                # idea to "flatten out" the generic params is too crazy (and supporting the same behaviour in function defs means losing auto function arg deduction (more spamming decltype would maybe fix)
                # dependent_class = cx.lookup_class(b.declared_type)
                # if dependent_class is not None and dependent_class.num_generic_params > 0:
                #     # TODO fix unique here
                #     deps = [gensym("C") for _ in range(dependent_class.num_generic_params)]
                #     typenames.extend(deps)
                #     decl = "std::shared_ptr<" + dependent_class.name_node.name + "<" + ", ".join(deps) + ">> " + b.name
                # else:
                decl = codegen_type(b, b.declared_type, inner_cx) + " " + b.name
                cpp += inner_indt + decl + ";\n\n"
                classdef.is_generic_param_index[block_index] = False
            else:
                t = gensym("C")
                typenames.append(t)
                decl = t + " " + b.name
                cpp += inner_indt + decl + ";\n\n"
                classdef.is_generic_param_index[block_index] = True
            uninitialized_attributes.append(b)
            uninitialized_attribute_declarations.append(decl)
        elif isinstance(b, Assign):
            # see how far this gets us
            # TODO fix simple assignments
            cpp += inner_indt + codegen_node(b, inner_cx) + ";\n\n"
        elif is_comment(b):
            cpp += codegen_node(b, inner_cx)
        else:
            raise CodeGenError("Unexpected expression in class body", b)

    if uninitialized_attributes:
        # autosynthesize constructor
        cpp += inner_indt + "explicit " + name.name + "(" + ", ".join(uninitialized_attribute_declarations) + ") : "
        cpp += ", ".join([a.name + "(" + a.name + ")" for a in uninitialized_attributes]) + " {}\n\n"
    # else:
    #     cpp += inner_indt + "explicit " + name.name + "() = default;\n\n"
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

    # TODO replace find_defs with handling in Scope
    cpp = "while (" + codegen_node(whilecall.args[0], cx.enter_scope()) + ") {"
    cpp += codegen_block(whilecall.args[1], cx.enter_scope())
    cpp += cx.indent_str() + "}\n"
    return cpp


def codegen_block(block: Block, cx):
    assert isinstance(block, Block)
    assert block.args
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
            # TODO be more strict here (but allowing non-identifier declarations allows e.g. "std.cout : using" and "boost::somesuch : using")
            declared_type = b.declared_type
            cpp += codegen_type(b, b.declared_type, cx)
            b.declared_type = None
            cpp += " " + codegen_node(b, cx) + ";\n"
            b.declared_type = declared_type
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

    for i, arg in enumerate(args):
        if arg.declared_type is None:
            raise CodeGenError("parameter types must be specified for interface methods")
        if not isinstance(arg, Identifier):
            raise CodeGenError("Only simple args allowed for interface method (you don't want c++ virtual functions with default arguments)")

        # TODO unify with codegen_def
        if cx.lookup_class(arg.declared_type) is not None:
            autoconst = "const "
            autoref = "&"
        else:
            autoconst = ""
            autoref = ""

        params.append(autoconst + codegen_type(arg, arg.declared_type, cx) + autoref + " " + str(arg))

    return "virtual {} {}({}) = 0;\n\n".format(return_type, name, ", ".join(params))


def autoconst(type_str: str):
    # return f"std::conditional_t<std::is_const_v<{type_str}>, {type_str}, const {type_str}>"
    # return "std::add_const_t<" + type_str + ">"
    # this is a nice idea that works with the testsuite right now but requires
    # a new keyword for e.g. taking a param by value or non-const reference
    # (disabling to lower mental overhead of 'unsafe' c++ integration code - 'safe' code should be fully generic or use the ourlang class/struct system anyway)
    return type_str


# def autoref(type_str: str):
#     # suprisingly compiles with a few examples (note that type_str would also be a conditional_t)but ends up warning about "const qualifier on reference type has no effect"
#     # return f"std::conditional_t<std::is_reference_v<{type_str}>, {type_str}, {type_str}&>"
#     # seem promising but not going to work
#     # return "std::add_lvalue_reference_t<" + type_str + ">"
#     # return f"std::conditional_t<is_smart_pointer<{type_str}>::value && std::is_base_of_v<{type_str}::element_type, object>, {type_str}&, {type_str}>"
#     return type_str  # can't do this for arbitrary types (even if something like the above works, going to make error messages sooo much worse.
#     # TODO if transpiler detects a class type e.g. Foo, add ref, otherwise not


def type_inorder_traversal(typenode: Node, func):
    if isinstance(typenode, TypeOp):
        if res := type_inorder_traversal(typenode.Lhs, func) is not None:
            return res
        return type_inorder_traversal(typenode.rhs, func)
    else:
        return func(typenode)


def codegen_def(defnode: Call, cx):
    assert defnode.func.name == "def"
    name_node = defnode.args[0]
    name = name_node.name
    args = defnode.args[1:]
    block = args.pop()
    assert isinstance(block, Block)
    return_type_node = defnode.declared_type

    if isinstance(name_node, Call) and name_node.func.name == "operator" and len(name_node.args) == 1 and isinstance(operator_name_node := name_node.args[0], StringLiteral):
        name = "operator" + operator_name_node.func  # TODO fix wonky non-node funcs and args, put raw string somewhere else

    if name is None:
        raise CodeGenError(f"can't handle name {name_node} in def {defnode}")

    params = []
    typenames = []

    is_destructor = False
    if name == "destruct" and isinstance(defnode.parent, Block) and isinstance(defnode.parent.parent, Call) and defnode.parent.parent.func.name == "class":
        class_identifier = defnode.parent.parent.args[0]
        assert isinstance(class_identifier, Identifier)
        class_name = class_identifier.name
        if args:
            raise CodeGenError("destructors can't take arguments")
        is_destructor = True

    is_interface_method = isinstance(name_node.declared_type, Call) and name_node.declared_type.func.name == "interface"
    has_non_trailing_return = name_node.declared_type is not None and not is_interface_method

    if is_interface_method and return_type_node is None:
        raise CodeGenError("must specify return type of interface method")

    for i, arg in enumerate(args):
        if is_interface_method:
            if arg.declared_type is None:
                raise CodeGenError("parameter types must be specified for interface methods")
            if not isinstance(arg, Identifier):
                raise CodeGenError("Only simple args allowed for interface method (c++ virtual functions with default arguments are best avoided)")

        if arg.declared_type is not None:
            if isinstance(arg, Identifier):
                if cx.lookup_class(arg.declared_type) is not None:
                    params.append("const " + codegen_type(arg, arg.declared_type, cx) + "& " + str(arg))
                else:
                    params.append(autoconst(codegen_type(arg, arg.declared_type, cx)) + " " + str(arg))
            else:
                # params.append(autoconst(autoref(codegen_type(arg, arg.declared_type, cx))) + " " + codegen_node(arg, cx))
                # note precedence change making
                raise SemanticAnalysisError("unexpected typed expr in defs parameter list", arg)
                # TODO: list typing needs fix after : precedence change
        elif isinstance(arg, Assign) and not isinstance(arg, NamedParameter):
            raise SemanticAnalysisError("Overparenthesized assignments in def parameter lists are not treated as named params. To fix, remove the redundant parenthesese from:", arg)
        elif isinstance(arg, NamedParameter):
            if not isinstance(arg.lhs, Identifier):
                raise SemanticAnalysisError(
                    "Non identifier left hand side in def arg", arg)

            if arg.lhs.declared_type is not None:
                # params.append(autoconst(autoref(codegen_node(arg.lhs.declared_type))) + arg.lhs.name + " = " + codegen_node(arg.rhs, cx))
                if cx.lookup_class(arg.lhs.declared_type) is not None:
                    # this only succeeds for literal Foo (not const: Foo: ref)
                    # (so no possibility of double adding 'const' - plus can already create a by-value param of class type using std::remove_const)
                    params.append("const " + codegen_type(arg.lhs, arg.lhs.declared_type, cx) + arg.lhs.name + "& = " + codegen_node(arg.rhs, cx))
                else:
                    params.append(
                        # autoconst(
                        codegen_type(arg.lhs, arg.lhs.declared_type, cx)#)
                    + arg.lhs.name + " = " + codegen_node(arg.rhs, cx))

            elif isinstance(arg.rhs, ListLiteral):
                if not arg.rhs.args:
                    params.append("const std::vector<" + vector_decltype_str(arg, cx) + ">&" + arg.lhs.name + " = {" + ", ".join([codegen_node(a, cx) for a in arg.rhs.args]) + "}")
                else:
                    # the above (our own poor reimplementation of CTAD with a bit of extra forward type inference) works but we can just use CTAD:

                    # c++ gotcha - not usable as a default argument!
                    # params.append("const auto& " + arg.lhs.name + " = std::vector {" + ", ".join(
                    #         [codegen_node(a, cx) for a in arg.rhs.args]) + "}")

                    # inferred part still relies on CTAD:
                    vector_part = "std::vector {" + ", ".join([codegen_node(a, cx) for a in arg.rhs.args]) + "}"

                    # but it's now usable as a default argument:
                    params.append("const decltype(" + vector_part + ")& " + arg.lhs.name + " = " + vector_part)
            elif isinstance(arg.rhs, Call) and arg.rhs.func.name == "lambda":
                # params.append("auto " + codegen_node(arg.lhs, cx) + "= " + codegen_node(arg.rhs, cx))
                assert 0  # need to autoconvert to std::function
            else:
                # if isinstance(arg.lhs, Identifier):
                # auto insertion of const & here might be problematic
                # params.append("const " + decltype_str(arg.rhs, cx) + "& " + str(arg.lhs) + " = " + codegen_node(arg.rhs, cx))

                # note that this adds const& to lhs for known class constructor calls e.g. Foo() but note e.g. even if Foo() + 1 returns Foo, no automagic const& added
                if isinstance(arg.rhs, Call) and cx.lookup_class(arg.rhs.func) is not None:
                    # it's a known class (object derived). auto add const&
                    # (though std::add_const_t works here, we can be direct)
                    make_shared = codegen_node(arg.rhs, cx)
                    # (we can also be direct with the decltype addition as well though decltype_str works now)
                    params.append("const decltype(" + make_shared + ") " + arg.lhs.name + "& = " + make_shared)
                else:
                    params.append(autoconst(decltype_str(arg.rhs, cx)) + arg.lhs.name + " = " + codegen_node(arg.rhs, cx))
                # else:
                #     raise SemanticAnalysisError(
                #         "Non identifier left hand side in def arg", arg)
                #     # params.append("const " + decltype_str(arg.rhs, cx) + "& " + codegen_node(arg.lhs, cx) + " = " + codegen_node(arg.rhs, cx))

        else:
            t = "T" + str(i + 1)
            # params.append(t + "&& " + arg.name)
            # params.append(t + " " + arg.name)
            params.append("const " + t + "& " + arg.name)
            typenames.append("typename " + t)

    template = ""
    inline = "inline "
    non_trailing_return = ""
    if has_non_trailing_return:
        non_trailing_return_node = name_node.declared_type
        non_trailing_return = " " + codegen_type(name_node, non_trailing_return_node, cx) + " "
        def is_template_test(expr):
            return isinstance(expr, Template) and expr.func.name == "template"
        if list(find_all(non_trailing_return_node, test=is_template_test)):
            if len(typenames) > 0:
                raise CodeGenError("Explicit template function with generic params", defnode)
            template = ""
        # inline = ""  # debatable whether a non-trailing return should inmply no "inline":
        # TODO?: tvped func above a certain complexity threshold automatically placed in synthesized implementation file

    elif is_interface_method:
        assert len(typenames) == 0
        template = ""
        inline = ""
    if typenames:
        template = "template <{0}>\n".format(", ".join(typenames))
        inline = ""

    if name == "main":
        if return_type_node or has_non_trailing_return:
            raise CodeGenError("main implicitly returns int. no explicit return type or directives allowed.", defnode)
        template = ""
        inline = ""
        if not isinstance(defnode.parent, Module):
            raise CodeGenError("unexpected nested main function", defnode)
        defnode.parent.has_main_function = True

    if return_type_node is not None:
        # return_type = codegen_type(name_node, name_node.declared_type)
        return_type = codegen_type(defnode, return_type_node, cx)
        if is_destructor:
            raise CodeGenError("destruct methods can't specifiy a return type")
    elif name == "main":
        return_type = "int"
    else:
        return_type = "auto"
        found_return = False
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
        # not marked virtual because inheritance not implimented yet (note that interface abcs have a virtual destructor)
        funcdef = "~" + class_name + "()"
    else:
        funcdef = "{}{}{}auto {}({}) -> {}".format(template, non_trailing_return, inline, name, ", ".join(params), return_type)
        if is_interface_method:
            funcdef += " override" # maybe later: use final if method not 'overridable'

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

        if replace_self and isinstance(s.parent, AttributeAccess) and s.parent.lhs is s:
            # rewrite as this->foo:
            this = RebuiltIdentifer("this")
            arrow = ArrowOp(args=[this, s.parent.rhs])
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

    indt = cx.indent_str()
    block_cx = cx.enter_scope()
    block_cx.in_function_body = True
    block_str = codegen_block(block, block_cx)

    if need_self:
        # (note: this will be a compile error in a non-member function / non-shared_from_this deriving class)
        block_str = block_cx.indent_str() + "const auto self = ceto::shared_from(this);\n" + block_str

    # if not is_destructor and not is_return(block.args[-1]):
    #     block_str += block_cx.indent_str() + "return {};\n"
    # no longer doing this^

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
            raise CodeGenError("Unexpected lambda argument", a)
        if a.declared_type is not None:
            param = codegen_type(a, a.declared_type, cx) + " " + a.name
        else:
            # TODO same const ref by default etc behaviour as "def"
            param = "auto " + a.name
        params.append(param)
    newcx = cx.enter_scope()
    newcx.in_function_body = True
    declared_type = None
    type_str = ""
    if node.declared_type is not None:
        type_str = " -> " + codegen_type(node, node.declared_type, cx)
    # if isinstance(node.func, ArrowOp):
    #     # not workable for precedence reasons
    #     if declared_type is not None:
    #         raise CodeGenError("Multiple return types specified for lambda?", node)
    #     declared_type = node.func.rhs
    #     # simplify AST (still messed with for 'is return type void?' stuff)
    #     node.declared_type = declared_type  # put type in normal position
    #     node.func = node.func.lhs  # func is now 'lambda' keyword

    if cx.parent.in_function_body:

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

        # this should use Scope
        possible_captures = []
        for i in idents:
            if i.name == "self":
                possible_captures.append(i.name)
            elif d := find_def(i):
                defnode, defcontext = d
                is_capture = True
                while is_capture and defnode is not None:
                    if defnode is node:
                        # defined in lambda or by lambda params (not a capture)
                        is_capture = False
                    defnode = defnode.parent
                if is_capture:
                    possible_captures.append(i.name)

        capture_list = ",".join([i + " = " + "ceto::default_capture(" + i + ")" for i in possible_captures])
    # elif TODO is nonescaping or immediately invoked:
    #    capture_list = "&"
    else:
        capture_list = ""
    # TODO:
    # lambda[ref](foo(x))
    # lambda[&x=x, y=bar(y)](foo(x,y))  # need to loosen ArrayAccess

    return ("[" + capture_list + "](" + ", ".join(params) + ")" + type_str + " {\n" +
            codegen_block(block, newcx) + newcx.indent_str() + "}")


def codegen(expr: Node):
    assert isinstance(expr, Module)
    cx = Scope()
    s = codegen_node(expr, cx)
    s = cpp_preamble + s
    print(s)
    return s


# should probably adjust the callers of decltype_str instead of this hackery
class _NoDeclTypeNeeded(Exception):
    def __init__(self, result):
        self.result = result


def decltype_str(node, cx):
    if isinstance(node, ArrayAccess):
        if not isinstance(node.func, Identifier):
            assert False

        for n, c in find_defs(node.func):
            if isinstance(c, Assign):# and hasattr(c.rhs, "_element_decltype_str"):
                if vds := vector_decltype_str(c, cx):
                    return vds

        return "decltype({})::value_type".format(str(node.func))

    elif isinstance(node, ListLiteral):

        return "std::vector<" + decltype_str(node.args[0], cx) + ">"

    else:
        try:
            return "decltype({})".format(_decltype_str(node, cx))
        except _NoDeclTypeNeeded as n:
            return n.result


def _decltype_str(node, cx):

    if isinstance(node, IntegerLiteral):
        return str(node)
    elif isinstance(node, StringLiteral):
        # return "std::declval(" + str(node) + "sv" + ")"
        return "std::string {" + str(node) + "}"

    if isinstance(node, BinOp):
        binop = node
        return _decltype_str(binop.lhs, cx) + str(binop.func) + _decltype_str(binop.rhs, cx)
    elif isinstance(node, UnOp):
        return "(" + str(node.func) + _decltype_str(node.args[0], cx) + ")"  # the other place unop is parenthesized is "necessary". here too?
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
            args_str = "(" + ", ".join([codegen_node(a, cx) for a in node.args]) + ")"
            class_name = "decltype(" + class_name + args_str + ")"

            if isinstance(class_node.declared_type,
                          Identifier) and class_node.declared_type.name == "unique":
                func_str = "std::unique_ptr<" + class_name + ">"
            else:
                func_str = "std::shared_ptr<" + class_name + ">"

            raise _NoDeclTypeNeeded(func_str)

        else:
            return codegen_node(call.func, cx) + "(" + ", ".join([_decltype_str(a, cx) for a in call.args]) + ")"
    elif isinstance(node, ListLiteral):
        return "std::vector<" + decltype_str(node.args[0], cx) + "> {}"

    assert isinstance(node, Identifier)

    defs = list(find_defs(node))
    if not defs:
        return str(node)

    for def_node, def_context in defs:
        if def_node.declared_type:
            raise _NoDeclTypeNeeded(codegen_type(def_node, def_node.declared_type, cx))

    last_ident, last_context = defs[-1]

    if isinstance(last_context, Assign):
        assign = last_context

        return _decltype_str(assign.rhs, cx)

    elif isinstance(last_context, Call) and last_context.func.name == "for":
        instmt = last_context.args[0]
        if not isinstance(instmt, BinOp) and instmt.func == "in":
            raise CodeGenError("for loop should have in-statement as first argument ", last_context)
        if last_ident is instmt.lhs:  # maybe we should adjust find_defs to return the in-operator ?
            return "std::declval<typename std::remove_reference_t<std::remove_const_t<" + decltype_str(instmt.rhs, cx) + ">>::value_type>()"

    else:
        return codegen_node(last_ident, cx)


def vector_decltype_str(node, cx):
    rhs_str = None
    found_use = False

    if isinstance(node, Assign) and isinstance(node.rhs, ListLiteral) and node.rhs.args:
        return decltype_str(node.rhs.args[0], cx)

    for found_use_node in find_uses(node):
        found_use = True
        parent = found_use_node.parent
        while rhs_str is None and not isinstance(parent, Block):
            found_use_context = parent

            if isinstance(found_use_context, AttributeAccess) and (
               found_use_context.lhs is found_use_node and found_use_context.rhs.name == "append"):

                append_call_node = None
                if isinstance(found_use_context.parent, Call) and len(found_use_context.parent.args) == 1:
                    append_arg = found_use_context.parent.args[0]

                    rhs_str = decltype_str(append_arg, cx)

            parent = parent.parent

        if rhs_str is not None:
            break
    if rhs_str is None:
        if found_use:
            # raise CodeGenError("list error, dunno what to do with this:", node)
            print("list error, dunno what to do with this:", node)
        else:
            raise CodeGenError("Unused empty list in template codegen", node)
    return rhs_str


def _shared_ptr_str_for_type(type_node, cx):
    if not isinstance(type_node, Identifier):
        return None

    name = type_node.name

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
    if isinstance(lhs, Identifier) and isinstance(rhs, StringLiteral) and lhs.name == "extern" and rhs.func == "C":
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
            if not isinstance(r, Identifier) or r.name != "const":
                raise CodeGenError("Invalid specifier for class type")
            if c.is_unique:
                return "const std::unique_ptr<const " + l.name + ">"
            return "std::shared_ptr<const " + l.name + ">"





def codegen_type(expr_node, type_node, cx, _is_leading=True):

    if isinstance(expr_node, (ScopeResolution, AttributeAccess)) and type_node.name == "using":
        pass
    elif not isinstance(expr_node, (ListLiteral, Identifier, Call, TypeOp)):
        raise CodeGenError("unexpected typed expression", expr_node)

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

    if not isinstance(type_node, (Identifier, Call, TypeOp, Template, AttributeAccess, ScopeResolution)):
        raise CodeGenError("unexpected type", type_node)

    return codegen_node(type_node, cx)


def codegen_node(node: Node, cx: Scope):
    assert isinstance(node, Node)

    if node.declared_type and not isinstance(node, (Assign, Call, ListLiteral)):
        if not isinstance(node, Identifier):
            raise CodeGenError("unexpected typed construct", node)

        return codegen_type(node, node, cx)  # this is a type inside a more complicated expression e.g. std.is_same_v<Foo, int:ptr>

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
        if isinstance(node.func, Identifier):
            func_name = node.func.name
            if func_name == "if":
                return codegen_if(node, cx)
            elif func_name == "def":
                raise CodeGenError("nested def not yet implemented")
            elif func_name == "lambda" or (isinstance(node.func, ArrowOp) and node.lhs.name == "lambda"):
                newcx = cx.enter_scope()
                newcx.in_function_param_list = True
                return codegen_lambda(node, newcx)
            elif func_name == "range":
                if len(node.args) == 1:
                    return "std::views::iota(0, " + codegen_node(node.args[0], cx) + ")"
                    # return "std::ranges:iota_view(0, " + codegen_node(node.args[0], cx) + ")"
                elif len(node.args) == 2:
                    return "std::views::iota(" + codegen_node(node.args[0], cx) + ", " + codegen_node(node.args[1], cx) + ")"
                    # return "std::ranges:iota_view(" + codegen_node(node.args[0], cx) + ", " + codegen_node(node.args[1], cx) + ")"
                else:
                    raise CodeGenError("range args not supported:", node)
            elif func_name == "operator" and len(node.args) == 1 and isinstance(operator_name_node := node.args[0], StringLiteral):
                return "operator" + operator_name_node.func  # TODO fix wonky non-node funcs and args, put raw string somewhere else
            else:
                arg_strs = [codegen_node(a, cx) for a in node.args]
                args_inner = ", ".join(arg_strs)
                args_str = "(" + args_inner + ")"

                # TODO we should re-enable this and leave "call_or_construct" only for "importing" raw but ceto-generated c++ code (would also require sprinkling conditional_t everywhere)
                if 0:# and class_def := cx.lookup_class(node.func):
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

                    if isinstance(class_node.declared_type, Identifier) and class_node.declared_type.name == "unique":
                        func_str = "std::make_unique<" + class_name + ">"
                    else:
                        func_str = "std::make_shared<" + class_name + ">"
                else:
                    pass

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
                        isinstance(node.parent, (ScopeResolution, ArrowOp, AttributeAccess)) and
                        node.parent.lhs is not node):
                    if func_str == "decltype":
                        cx.in_decltype = True
                    return simple_call_str

                dt_str = "decltype(" + simple_call_str + ")"

                simple_return = "return "
                if isinstance(node.parent, Block):
                    simple_return = ""

                call_str = "[" + capture + "] { if constexpr (std::is_base_of_v<ceto::object, " + dt_str + ">) { return ceto::call_or_construct<" + dt_str + ">" + args_str + "; } else { " + simple_return + simple_call_str + "; } } ()"

                return call_str
        else:
            # wrong precedence:
            # if isinstance(operator_node := node.func, Call) and operator_node.func.name == "operator" and len(operator_node.args) == 1 and isinstance(operator_name_node := operator_node.args[0], StringLiteral):
            #     func_str = "operator" + operator_name_node.func  # TODO fix wonky non-node funcs and args, put raw string somewhere else
            # else:
            #     func_str = codegen_node(node.func, cx)

            # not auto-flattening args is becoming annoying!
            # TODO make bin-op arg handling more ergonomic - maybe flatten bin-op args earlier (look at e.g. sympy's Add/Mul handling)
            method_name = None
            if isinstance(node.func, (AttributeAccess, ScopeResolution)):
                method_name = node.func.rhs
                while isinstance(method_name, (AttributeAccess, ScopeResolution)):
                    method_name = method_name.rhs

            func_str = None

            if method_name is not None:

                # assert isinstance(method_name, Identifier)

                # modify node.func
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

                if method_name.name == "operator" and len(node.args) == 1 and isinstance(operator_name_node := node.args[0], StringLiteral):
                    consume_method_name()
                    return "ceto::mad(" + codegen_node(node.func, cx) + ")->operator" + operator_name_node.func  # TODO fix wonky non-node funcs and args, put raw string somewhere else

                elif not isinstance(method_name.parent, (ScopeResolution, ArrowOp)):
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
                            for d in find_defs(node.func):
                                # print("found def", d, "when determining if an append is really a push_back")
                                if isinstance(d[1], Assign) and isinstance(d[1].rhs, ListLiteral):
                                    is_list = True
                                    break
                        if is_list:
                            append_str = "push_back"

                        func_str = "ceto::mad(" + codegen_node(node.func, cx) + ")->" + append_str
                    else:

                        # TODO fix AttributeAccess logic repeated here
                        if isinstance(node.func, Identifier) and (node.func.name == "std" or cx.lookup_class(node.func)):
                            func_str = node.func.name + "::" + codegen_node(method_name, cx)
                        else:
                            func_str = "ceto::mad(" + codegen_node(node.func, cx) + ")->" + codegen_node(method_name, cx)

            if func_str is None:
                func_str = codegen_node(node.func, cx)

            return func_str + "(" + ", ".join(map(lambda a: codegen_node(a, cx), node.args)) + ")"

    elif isinstance(node, IntegerLiteral):
        return str(node)
    elif isinstance(node, Identifier):
        name = node.name

        if name == "ptr":
            raise CodeGenError("Use of 'ptr' outside type context is an error", node)
        elif name == "ref":
            raise CodeGenError("Use of 'ref' outside type context is an error", node)
        elif name == "string":
            return "std::string"
        # elif name == "None":  # just use 'nullptr' (fine even in pure python syntax)
        #     return "nullptr"
        elif name == "dotdotdot":
            return "..."
        # elif name == "object":
        #     return "std::shared_ptr<object>"

        if not (isinstance(node.parent, (AttributeAccess, ScopeResolution)) and
                node is node.parent.lhs) and (
           ptr_name := _shared_ptr_str_for_type(node, cx)):
            return ptr_name + "<" + name + ">"

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
                        return "if constexpr (!std::is_void_v<decltype(" + ret_body + ")>" + declared_type_constexpr + ") { return " + ret_body + "; } else { " + ret_body + "; }"
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


        elif isinstance(node, Assign) and isinstance(node.lhs, Identifier):
            is_lambda_rhs_with_return_type = False

            if node.declared_type is not None and isinstance(node.rhs, Call) and node.rhs.func.name == "lambda":
                # TODO lambda return types need fixes
                lambdaliteral = node.rhs
                is_lambda_rhs_with_return_type = True
                # type of the assignment (of a lambda literal) is the type of the lambda not the lhs
                if lambdaliteral.declared_type is not None:
                    raise CodeGenError("Two return types defined for lambda:", node.rhs)
                lambdaliteral.declared_type = node.declared_type
                newcx = cx.enter_scope()
                newcx.in_function_param_list = True
                rhs_str = codegen_lambda(lambdaliteral, newcx)
            elif node.lhs.declared_type is None and isinstance(node.rhs, ListLiteral) and not node.rhs.args and node.rhs.declared_type is None:
                # handle untyped empty list literal by searching for uses
                rhs_str = "std::vector<" + vector_decltype_str(node, cx) + ">()"
            else:
                rhs_str = codegen_node(node.rhs, cx)

            if isinstance(node.lhs, Identifier):
                lhs_str = node.lhs.name
                if node.lhs.declared_type:
                    lhs_type_str = codegen_type(node.lhs, node.lhs.declared_type, cx)
                    decl_str = lhs_type_str + " " + lhs_str

                    plain_initialization = decl_str + " = " + rhs_str

                    if isinstance(node.rhs, BracedLiteral):
                        # aka "copy-list-initialization" in this case
                        return plain_initialization

                    # prefer brace initialization to disable narrowing conversions (in these assignments):

                    direct_initialization = lhs_type_str + " " + lhs_str + " { " + rhs_str + " } "

                    # ^ but there are still cases where this introduces 'unexpected' aggregate initialization
                    # e.g. l2 : std.vector<std.vector<int>> = 1
                    # should it be printed as std::vector<std::vector<int>> l2 {1} (fine: aggregate init) or std::vector<std::vector<int>> l2 = 1  (error) (same issue if e.g. '1' is replaced by a 1-D vector of int)
                    # I think the latter behaviour for aggregates is less suprising: = {1} can be used if the aggregate init is desired.

                    if any(find_all(node.lhs.declared_type, test=lambda n: n.name == "auto")):  # this will fail when/if we auto insert auto more often (unless handled earlier via node replacement)
                        return direct_initialization

                    # printing of UnOp is currently parenthesized due to FIXME current use of pyparsing infix_expr discards parenthesese in e.g. (&x)->foo()   (the precedence is correct but whether explicit non-redundant parenthesese are used is discarded)
                    # this unfortunately can introduce unexpected use of overparethesized decltype (this may be a prob in other places although note use of remove_cvref etc in 'list' type deduction.
                    # FIXME: this is more of a problem in user code (see test changes). Also, current discarding of RedundantParens means user code can't explicitly call over-parenthesized decltype)
                    # for now with this case, just ensure use of non-overparenthesized version via regex:
                    rhs_str = re.sub(r'^\((.*)\)$', r'\1', rhs_str)

                    if isinstance(node.rhs, IntegerLiteral) or (isinstance(node.rhs, Identifier) and node.rhs.name in ["true", "false"]):  # TODO float literals
                        return f"{direct_initialization}; static_assert(std::is_convertible_v<decltype({rhs_str}), decltype({node.lhs.name})>)"

                    # So go given the above, define our own no-implicit-conversion init (without the gotcha for aggregates from naive use of brace initialization everywhere). Note that typed assignments in non-block / expression context will fail on the c++ side anyway so extra statements tacked on via semicolon is ok here.

                    # note that 'plain_initialization' will handle cvref mismatch errors!
                    return f"{plain_initialization}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype({rhs_str}), std::remove_cvref_t<decltype({node.lhs.name})>>)"

            else:
                lhs_str = codegen_node(node.lhs, cx)

            assign_str = " ".join([lhs_str, node.func, rhs_str])

            if not hasattr(node, "already_declared") and find_def(node.lhs) is None:
                if cx.in_function_body:
                    assign_str = "auto " + assign_str
                else:
                    # for global case we should probably print all typed assignments as constexpr (not just python style untyped ones)
                    assign_str = "constexpr auto " + assign_str

            return assign_str
        else:
            binop_str = None

            separator = " "

            if isinstance(node, AttributeAccess) and not isinstance(node, (ScopeResolution, ArrowOp)):

                if isinstance(node.lhs, Identifier) and (node.lhs.name == "std" or
                                                         cx.lookup_class(node.lhs)):
                    return node.lhs.name + "::" + codegen_node(node.rhs, cx)

                separator = ""

            elif is_comment(node):
                # probably needs to go near method handling logic now that precedence issue fixed (TODO re-enable comment stashing)
                if not (len(node.rhs.args) == 1 or isinstance(node.rhs.args[0], StringLiteral)):
                    raise CodeGenError("unexpected ceto::comment ", node)
                return "//" + node.rhs.args[0].func.replace("\n", "\\n") + "\n"

            if binop_str is None:

                if isinstance(node, AttributeAccess) and not isinstance(node, ScopeResolution):
                    binop_str = "ceto::mad(" + codegen_node(node.lhs, cx) + ")->" + codegen_node(node.rhs, cx)
                else:
                    funcstr = node.func  # fix ast: should be Ident
                    if node.func == "and":  # don't use the weird C operators tho tempting
                        funcstr = "&&"
                    elif node.func == "or":
                        funcstr = "||"
                    binop_str = separator.join([codegen_node(node.lhs, cx), funcstr, codegen_node(node.rhs, cx)])

            if isinstance(node.parent, (BinOp, UnOp)) and not isinstance(node.parent, (ScopeResolution, ArrowOp, AttributeAccess)):
                # guard against precedence mismatch (e.g. extra parenthesese
                # not strictly preserved in the ast)
                # untested / maybe-buggy
                binop_str = "(" + binop_str + ")"

            return binop_str

    elif isinstance(node, ListLiteral):

        list_type = node.declared_type
        # if list_type is None and isinstance(node.parent, Assign):
        #     list_type = node.parent.declared_type or node.parent.rhs.declared_type or node.parent.lhs.declared_type
        # lang design change: element type must be on rhs always
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
    elif isinstance(node, CStringLiteral):
        return str(node)
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
            # bad idea?: look at the uses of vars defined by string literals, they're const char* if they flow to C lib
            return str(node)  # const char * !
        return "std::string {" + str(node) + "}"
    # elif isinstance(node, RedundantParens):  # too complicated letting codegen deal with this. just disable -Wparens
    #     return "(" + codegen_node(node.args[0]) + ")"
    elif isinstance(node, Template):
        # allow auto shared_ptr etc with parameterized classes e.g. f : Foo<int> results in shared_ptr<Foo<int>> f not shared_ptr<Foo><int>(f)
        # (^ this is a bit of a dubious feature when e.g. f: decltype(Foo(1)) works without this special case logic)
        template_args = "<" + ",".join([codegen_node(a, cx) for a in node.args]) + ">"
        if ptr_name := _shared_ptr_str_for_type(node.func, cx):
            return ptr_name + "<" + node.func.name + template_args + ">"
        else:
            return codegen_node(node.func, cx) + template_args

    assert False, "unhandled node"

