from typing import Union, Any

from semanticanalysis import Node, Module, Call, Block, UnOp, BinOp, \
    ColonBinOp, Assign, NamedParameter, Identifier, IntegerLiteral, IfNode, \
    SemanticAnalysisError, SyntaxColonBinOp, find_def, find_use, find_uses, \
    find_all, find_defs
from parser import ListLiteral, TupleLiteral, ArrayAccess, StringLiteral, AttributeAccess


import io


class CodeGenError(Exception):
    pass

cpp_preamble = """
#include <memory>
#include <cstdio>
#include <vector>


struct object {
    virtual ~object() {
    };
};

"""


# Uses code and ideas from https://github.com/lukasmartinelli/py14

# https://brevzin.github.io/c++/2019/12/02/named-arguments/


def codegen_if(ifcall : Call, indent):
    assert isinstance(ifcall, Call)
    assert ifcall.func.name == "if"

    ifnode = IfNode(ifcall.func, ifcall.args)

    indt = ("    " * indent)

    scopes = [ifnode.cond, ifnode.thenblock, ifnode.elseblock]
    for elifcond, elifblock in ifnode.eliftuples:
        scopes.append(elifcond)
        scopes.append(elifblock)

    assigns = []

    def stop(n):
        return isinstance(n, Block) and n.parent.func.name not in ["if", "while"]

    for scope in scopes:
        assigns.extend(find_all(scope, test=lambda n: isinstance(n, Assign), stop=stop))

    print("all if assigns", list(assigns))

    declarations = {}

    for assign in assigns:
        if hasattr(assign, "already_declared"):
            continue
        if isinstance(assign.lhs, Identifier) and not find_def(assign.lhs):
            assign.already_declared = True
            if assign.lhs.name in declarations:
                continue
            declarations[codegen_node(assign.lhs)] = codegen_node(assign.rhs)

    cpp = ""
    for lhs in declarations:
        cpp += f"decltype({declarations[lhs]}) {lhs};\n" + indt

    cpp += "if (" + codegen_node(ifnode.cond) + ") {\n"
    cpp += codegen_block(ifnode.thenblock, indent + 1)

    for elifcond, elifblock in ifnode.eliftuples:
        cpp += indt + "} else if (" + codegen_node(elifcond, indent) + ") {\n"
        cpp += codegen_block(elifblock, indent + 1)

    if ifnode.elseblock:
        cpp += indt + "} else {\n"
        cpp += codegen_block(ifnode.elseblock, indent + 1)

    cpp += indt + "}"

    return cpp


def codegen_block(block: Block, indent):
    assert isinstance(block, Block)
    assert block.args
    cpp = ""
    indent_str = "    " * indent


    for b in block.args:
        cpp += indent_str + codegen_node(b, indent) + ";\n"
        # if isinstance(b, Call):
        #     if b.func.name == "if":
        #         cpp += codegen_if(b)
        # elif isinstance(b, BinOp):
        #     pass
        # elif isinstance(b, UnOp):
        #     pass

    if isinstance(block.parent, Call) and block.parent.func.name == "def":
        last_statement = block.args[-1]

        if not ((isinstance(last_statement, ColonBinOp) and last_statement.lhs.name == "return") or (isinstance(last_statement, Identifier) and last_statement.name == "return")):
            cpp += indent_str + "return {};\n"

    return cpp


# def indent(text, amount, ch=' '):
    # return textwrap.indent(text, amount * ch)


def codegen_def(defnode: Call, indent):
    assert defnode.func.name == "def"
    name_node = defnode.args[0]
    name = name_node.name
    args = defnode.args[1:]
    block = args.pop()
    assert isinstance(block, Block)

    params = []
    typenames = []
    for i, arg in enumerate(args):
        if arg.declared_type is not None:
            params.append(str(arg.declared_type) + " " + codegen_node(arg))
        elif isinstance(arg, Assign) and not isinstance(arg, NamedParameter):
            raise SemanticAnalysisError("Overparenthesized assignments in def parameter lists are not treated as named params. To fix, remove the redundant parenthesese from:", arg)
        elif isinstance(arg, NamedParameter):
            if isinstance(arg.rhs, ListLiteral):
                params.append("std::vector<" + vector_decltype_str(arg) + ">" + codegen_node(arg.lhs) + " = {" + ", ".join([codegen_node(a) for a in arg.rhs.args]) + "}")
                # if arg.rhs.args:
                #     valuepart = "= " + codegen_node(arg.rhs)
                #     declpart = decltype_str(arg.rhs) + " " + codegen_node(arg.lhs)
                # else:
                #     valuepart = ""
                #     declpart = "std::vector<" + decltype_str(arg.rhs) + "> " + codegen_node(arg.lhs)
                #
                # # params.append((decltype_str(arg.rhs) + " " + codegen_node(arg.lhs), "= " + codegen_node(arg.rhs)))
                # params.append((declpart, valuepart))
            elif isinstance(arg.rhs, Call) and arg.rhs.func.name == "lambda":
                params.append("auto " + codegen_node(arg.lhs) + "= " + codegen_node(arg.rhs))
            else:
                params.append(decltype_str(arg.rhs) + " " + codegen_node(arg.lhs) + "= " + codegen_node(arg.rhs))

        else:
            t = "T" + str(i + 1)
            params.append(t + " " + arg.name)
            typenames.append("typename " + t)

    template = "inline "
    if name == "main":
        template = ""
    if typenames:
        template = "template <{0}>\n".format(", ".join(typenames))

    if name_node.declared_type is not None:
        return_type = str(name_node.declared_type)  # brittle
    elif name == "main":
        return_type = "int"
    else:
        return_type = "auto"

    defnode.cpp_return_type = return_type
    funcdef = "{} auto {}({}) -> {}".format(template, name, ", ".join(params), return_type)

    return funcdef + " {\n" + codegen_block(block, indent + 1) + "}\n\n"


def codegen_lambda(node, indent):
    args = list(node.args)
    block = args.pop()
    assert isinstance(block, Block)
    params = ["auto " + codegen_node(a) for a in args]
    indent += 1
    indt = "    " * indent
    return ("[](" + ", ".join(params) + ") {\n" +
            codegen_block(block, indent + 1) + indt + "}")


    # assert defnode.func.name == "def"
    # name = defnode.args[0]
    # cpp = io.StringIO()
    #
    # # template < typename T1, typename T2, typename T3 = decltype(5) >
    #
    #  # f"auto {name} ("
    # # cpp.write(f"std::shared_ptr<object> {name} (")
    # args = defnode.args[1:]
    # block = args.pop()
    # assert isinstance(block, Block)
    # template_preamble = ""
    # if len(args):
    #
    #     template_params = []
    #     for i, arg in enumerate(args, start=1):
    #         template_params.append(f"typename T{i} {arg.name}")
    #     template_preamble = "template <" + ", ".join(template_params) + ">"
    #     cpp_args = ", ".join([f" {a}" for a in args])
    #     cpp.write(cpp_args)

# unused
def _codegen_def_dynamic(defnode: Call):
    assert defnode.func.name == "def"
    name = defnode.args[0]
    cpp = io.StringIO()
    cpp.write(f"std::shared_ptr<object> {name} (")
    args = defnode.args[1:]
    block = args.pop()
    assert isinstance(block, Block)
    if len(args):
        cpp_args = ", ".join([f"std::shared_ptr<object> {a}" for a in args])
        cpp.write(cpp_args)
    cpp.write(") {\n")
    cpp.write(codegen_block(block))
    cpp.write("}")
    return cpp.getvalue()


def codegen(expr: Node):
    assert isinstance(expr, Module)
    s = codegen_node(expr)
    return cpp_preamble + s


def decltype(node):
    """Create C++ decltype statement"""
    if is_list(node):
        return "std::vector<decltype({0})>".format(value_type(node))
    else:
        return "decltype({0})".format(value_type(node))


def is_list(node):
    """Check if a node was assigned as a list"""
    if isinstance(node, ListLiteral):
        return True
    # elif isinstance(node, Assign):
    #     return is_list(node.rhs)  # dunno about this one
    elif isinstance(node, Identifier):
        # var = node.scopes.find(node.id)
        found_node, defining_context = find_def(node)
        if isinstance(defining_context, Assign) and is_list(defining_context.rhs):
            return True
        return (hasattr(var, "assigned_from") and not
        isinstance(var.assigned_from, ast.FunctionDef) and
                is_list(var.assigned_from.value))
    else:
        return False



def value_expr(node):
    """
    Follow all assignments down the rabbit hole in order to find
    the value expression of a name.
    The boundary is set to the current scope.
    """
    # return ValueExpressionVisitor().visit(node)


def value_type(node):
    """
    Guess the value type of a node based on the manipulations or assignments
    in the current scope.
    Special case: If node is a container like a list the value type inside the
    list is returned not the list type itself.
    """

    if not isinstance(node, Node):
        return
    elif isinstance(node, (IntegerLiteral, StringLiteral)):
        return value_expr(node)
    elif isinstance(node, Identifier):
        if node.name == 'True' or node.name == 'False':
            # return CLikeTranspiler().visit(node)
            return "true" if node.name == 'True' else "false"  # XXX??

            # var = node.scopes.find(node.id)
            found_node, defining_context = find_def(node)
            # if isinstance(defining_context, Assign) and is_list(
            #         defining_context.rhs):

            # if defined_before(var, node):
            #     return node.id
            # else:
            # return self.visit(var.assigned_from.value)

            # this is wrong
            return str(found_node)
            # return value_expr(found_node)

    # class ValueTypeVisitor(ast.NodeVisitor):
    #     def visit_Num(self, node):
    #         return value_expr(node)
    #
    #     def visit_Str(self, node):
    #         return value_expr(node)
    #
    #     def visit_Name(self, node):
    #         if node.id == 'True' or node.id == 'False':
    #             return CLikeTranspiler().visit(node)
    #
    #         var = node.scopes.find(node.id)
    #         if defined_before(var, node):
    #             return node.id
    #         else:
    #             return self.visit(var.assigned_from.value)
    #
    #     def visit_Call(self, node):
    #         params = ",".join([self.visit(arg) for arg in node.args])
    #         return "{0}({1})".format(node.func.id, params)
    #
    #     def visit_Assign(self, node):
    #         if isinstance(node.value, ast.List):
    #             if len(node.value.elts) > 0:
    #                 val = node.value.elts[0]
    #                 return self.visit(val)
    #             else:
    #                 target = node.targets[0]
    #                 var = node.scopes.find(target.id)
    #                 first_added_value = var.calls[0].args[0]
    #                 return value_expr(first_added_value)
    #         else:
    #             return self.visit(node.value)


# class ValueExpressionVisitor(ast.NodeVisitor):
#     def visit_Num(self, node):
#         return str(node.n)
#
#     def visit_Str(self, node):
#         return node.s
#
#     def visit_Name(self, node):
#         var = node.scopes.find(node.id)
#         if isinstance(var.assigned_from, ast.For):
#             it = var.assigned_from.iter
#             return "std::declval<typename decltype({0})::value_type>()".format(
#                    self.visit(it))
#         elif isinstance(var.assigned_from, ast.FunctionDef):
#             return var.id
#         else:
#             return self.visit(var.assigned_from.value)
#
#     def visit_Call(self, node):
#         params = ",".join([self.visit(arg) for arg in node.args])
#         return "{0}({1})".format(node.func.id, params)
#
#     def visit_Assign(self, node):
#         return self.visit(node.value)
#
#     def visit_BinOp(self, node):
#         return "{0} {1} {2}".format(self.visit(node.left),
#                                     CLikeTranspiler().visit(node.op),
#                                     self.visit(node.right))
#



# class ValueTypeVisitor(ast.NodeVisitor):
#     def visit_Num(self, node):
#         return value_expr(node)
#
#     def visit_Str(self, node):
#         return value_expr(node)
#
#     def visit_Name(self, node):
#         if node.id == 'True' or node.id == 'False':
#             return CLikeTranspiler().visit(node)
#
#         var = node.scopes.find(node.id)
#         if defined_before(var, node):
#             return node.id
#         else:
#             return self.visit(var.assigned_from.value)
#
#     def visit_Call(self, node):
#         params = ",".join([self.visit(arg) for arg in node.args])
#         return "{0}({1})".format(node.func.id, params)
#
#     def visit_Assign(self, node):
#         if isinstance(node.value, ast.List):
#             if len(node.value.elts) > 0:
#                 val = node.value.elts[0]
#                 return self.visit(val)
#             else:
#                 target = node.targets[0]
#                 var = node.scopes.find(target.id)
#                 first_added_value = var.calls[0].args[0]
#                 return value_expr(first_added_value)
#         else:
#             return self.visit(node.value)

def decltype_str(node):
    if isinstance(node, ArrayAccess):
        for n, c in find_defs(node.func):
            if isinstance(c, Assign):# and hasattr(c.rhs, "_element_decltype_str"):
                if vds := vector_decltype_str(c):
                    return vds
                # return c.rhs._element_decltype_str
            # print("array def", d)

        return "decltype({})::value_type".format(codegen_node(node.func))
    elif isinstance(node, ListLiteral):
        # never succeeded
        # if not node.args:
        #     if isinstance(node.parent, Assign):
        #         if vds := vector_decltype_str(node.parent):
        #             return vds

        return "std::vector<" + decltype_str(node.args[0]) + ">"
        # return vector_decltype_str(node)

        result = "" # "std::vector<"
        end = ">"
        ll = node#.args[0]

        while isinstance(ll, ListLiteral):
            result += "std::vector<" #+ _decltype_str(node.args[0])
            end += ">"
            ll = ll.args[0]

        result += decltype_str(ll)
        result += end

        # if isinstance(node.args[0], ListLiteral):
        #     return "std::vector<" + _decltype_str(node.args[0]) + ">"
        # else:
        #     return "std::vector<" + decltype_str(node.args[0]) + ">"
        return result

    else:
        return "decltype({})".format(_decltype_str(node))


def _decltype_str(node):

    if isinstance(node, (IntegerLiteral, StringLiteral)):
        return str(node)

    if isinstance(node, BinOp):
        binop = node
        return _decltype_str(binop.lhs) + str(binop.func) + _decltype_str(binop.rhs)
    elif isinstance(node, Call):
        call = node
        # if call.func.name == "lambda":
        #     return codegen_node(call)
        return codegen_node(call.func) + "(" + ", ".join([_decltype_str(a) for a in call.args]) + ")"
    # elif isinstance(node, ArrayAccess):
    #     return "decltype({})::value_type".format(codegen_node(node.func))
        # return "[&](){{ return {}; }}".format(codegen_node(node))
    elif isinstance(node, ListLiteral):
        # if isinstance(node.args[0], ListLiteral):
        #     return "std::vector<" + _decltype_str(node.args[0]) + ">"
        # else:
        #     return "std::vector<" + decltype_str(node.args[0]) + ">"
        return "std::vector<" + decltype_str(node.args[0]) + "> {}"
        # return _decltype_str(node.args[0])


    if not isinstance(node, Identifier):
        print("uh oh", node)
        assert 0

    defs = list(find_defs(node))
    if not defs:
        return str(node)

    for def_node, def_context in defs:
        if def_node.declared_type:
            return "std::declval<{}>()".format(def_node.declared_type)
        if isinstance(def_context, Assign) and def_context.declared_type:
            # return str(def_context.declared_type)
            return "std::declval<{}>()".format(def_context.declared_type)


    last_ident, last_context = defs[-1]

    # return decltype_str(last_ident)

    if isinstance(last_context, Assign):
        assign = last_context

        return _decltype_str(assign.rhs)

        if isinstance(assign.rhs, BinOp):
            # for arg in assign.rhs.args:
            #     if found := decltype_str(arg):
            #         return found
            binop = assign.rhs
            return decltype_str(binop.lhs) + str(binop.func) + decltype_str(binop.rhs)
        elif isinstance(assign.rhs, Call):
            call = assign.rhs
            return codegen_node(call.func) + "(" + ", ".join([decltype_str(a) for a in call.args]) + ")"
        else:
            print("hmm?1")
            return codegen_node(assign.rhs)
    else:
        print("hmm?2")
        return codegen_node(last_ident)




def codegen_node(node: Union[Node, Any], indent=0):
    cpp = io.StringIO()

    if isinstance(node, Module):
        for modarg in node.args:
            if modarg.func.name == "def":
                defcode = codegen_def(modarg, indent)
                cpp.write(defcode)
            else:
                print("probably should handle", modarg)
    elif isinstance(node, Call): # not at module level
        if isinstance(node.func, Identifier):
            if node.func.name == "if":
                cpp.write(codegen_if(node, indent))
            elif node.func.name == "def":
                print("need to handle nested def")
            elif node.func.name == "lambda":
                cpp.write(codegen_lambda(node, indent))
            else:
                cpp.write(node.func.name + "(" + ", ".join(map(codegen_node, node.args)) + ")")
        else:
            print("need to handle indirect call")

    elif isinstance(node, IntegerLiteral):
        cpp.write(str(node))
    elif isinstance(node, Identifier):
        if node.name == "None":
        #     cpp.write(r"{}") # tempting
            cpp.write("nullptr")
        else:
            cpp.write(str(node))
    # elif isinstance(node, UnOp):
        # if node.func == "return":  # TODO fix UnOp func should be an identifier (although UnOp return should be converted to ColonBinOp earlier - or removed from language)
        #     cpp.write("return")
    elif isinstance(node, BinOp):

        if isinstance(node, ColonBinOp):
            assert isinstance(node, SyntaxColonBinOp)  # sanity check type system isn't leaking
            if node.lhs.name == "return":
                cpp.write("return " + codegen_node(node.args[1]))
            else:
                assert False

        elif isinstance(node, Assign) and isinstance(node.lhs, Identifier):
            rhs_str = None

            # Handle template declaration for an empty list by searching for uses
            if isinstance(node.rhs, ListLiteral) and not node.rhs.args:
                rhs_str = "std::vector<" + vector_decltype_str(node) + ">()"

            else:
                rhs_str = codegen_node(node.rhs)

            assign_str = " ".join([codegen_node(node.lhs), node.func, rhs_str])

            if not hasattr(node, "already_declared") and find_def(node.lhs) is None:
                assign_str = "auto " + assign_str

            cpp.write(assign_str)
        else:
            binop_str = None

            separator = " "
            if isinstance(node, AttributeAccess):
                separator = ""

                if isinstance(node.rhs, Call) and node.rhs.func.name == "append":
                    apnd = node.rhs
                    assert len(apnd.args) == 1

                    is_list = False
                    if isinstance(node.lhs, ListLiteral):
                        is_list = True
                    else:
                        for d in find_defs(node.lhs):
                            if isinstance(d[1], Assign) and isinstance(d[1].rhs, ListLiteral):
                                is_list = True
                                break
                    if is_list:
                        binop_str = "{}.push_back({})".format(codegen_node(node.lhs), codegen_node(apnd.args[0]))

            if binop_str is None:
                cpp.write(separator.join([codegen_node(node.lhs), node.func, codegen_node(node.rhs)]))
            else:
                cpp.write(binop_str)

    elif isinstance(node, ListLiteral):
        if node.args:
            elements = [codegen_node(e) for e in node.args]
                # value_type = decltype(node.elts[0])



            # return "std::vector<decltype({})>{{{}}}".format(elements[0], ", ".join(elements))
            # return "std::vector<decltype([&](){{return {};}})>{{{}}}".format(decltype_str(node.args[0]), ", ".join(elements))
            return "std::vector<{}>{{{}}}".format(decltype_str(node.args[0]), ", ".join(elements))


        else:
            assert False
            return "{}" # lol hope this works

                # "std::vector<{0}>{{{1}}}""
            #
            # "std::vector<decltype({0})>".format(value_type(node))

            # return "std::vector<{0}>{{{1}}}".format(value_type,
            #                                         ", ".join(elements))

            raise CodeGenError("Cannot create vector without elements (in template generation mode)")
    elif isinstance(node, ArrayAccess):
        if len(node.args) > 1:
            raise CodeGenError("advanced slicing not supported yet")
        return codegen_node(node.func) + "[" + codegen_node(node.args[0]) + "]"
    elif isinstance(node, StringLiteral):
        return str(node)

    return cpp.getvalue()


def vector_decltype_str(node):
    rhs_str = None
    found_use = False

    if isinstance(node, Assign) and isinstance(node.rhs, ListLiteral) and node.rhs.args:
        return decltype_str(node.rhs.args[0])

    for found_use_node in find_uses(node):
        found_use = True
        parent = found_use_node.parent
        while rhs_str is None and not isinstance(parent, Block):
            found_use_context = parent

            if isinstance(found_use_context,
                          AttributeAccess) and found_use_context.lhs is found_use_node and isinstance(
                    found_use_context.rhs,
                    Call) and found_use_context.rhs.func.name == "append":
                apnd = found_use_context.rhs
                assert len(apnd.args) == 1
                apnd_arg = apnd.args[0]

                # for apnd_arg_def in find_defs(apnd_arg):

                val = decltype_str(apnd_arg)
                # using arrElemType = decltype([&](){return arr[0];}());
                # rhs_str = f"using arr_elem_type = decltype([&](){{return {val};}}());"
                # rhs_str = f"std::vector<decltype([&](){{return {val};}})>"
                # rhs_str = "std::vector<decltype({})>{{}}".format(val)
                # node.rhs._element_decltype_str = val

                rhs_str = "std::vector<{}>{{}}".format(val)
                rhs_str = val

                # if apnd_arg_defs := list(find_defs(apnd_arg)):
                #     apnd_arg_def_node, apnd_arg_def_context = apnd_arg_defs[-1]
                #     if apnd_arg_def_node.declared_type is not None:
                #         rhs_str = "std::vector<{}>{{}}".format(codegen_node(apnd_arg_def_node.declared_type),  # need to figure out printing of types...
                #                                                codegen_node(apnd.args[0]))
                #     elif isinstance(apnd_arg_def_context, Assign):
                #         rhs_str = "std::vector<decltype({})>{{}}".format(codegen_node(apnd_arg_def_context.rhs))
                #
                # if rhs_str is None:
                #     rhs_str = "std::vector<decltype({})>{{}}".format(codegen_node(apnd.args[0]))

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
