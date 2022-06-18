from semanticanalysis import Node, Module, Call, Block, UnOp, BinOp, ColonBinOp, Assign, NamedParameter, Identifier, IntegerLiteral, IfNode, SemanticAnalysisError
import io
import textwrap

cpp_preamble = """
#include <memory>
#include <cstdio>

class object {
    virtual ~{
    };
};

"""


def codegen(expr):
    assert isinstance(expr, Module)
    s = codegen_node(expr)
    return cpp_preamble + s


def codegen_node(node: Node):
    cpp = io.StringIO()

    if isinstance(node, Module):
        for modarg in node.args:
            if modarg.func.name == "def":
                defcode = codegen_def(modarg)
                cpp.write(defcode)
            else:
                print("probably should handle", modarg)
    elif isinstance(node, Call): # not at module level
        if isinstance(node.func, Identifier) and node.func.name == "if":
            cpp.write(codegen_if(node))
    elif isinstance(node, (Identifier, IntegerLiteral)):
        cpp.write(str(node))
    elif isinstance(node, BinOp):
        cpp.write(codegen_node(node.args[0]) + node.func + codegen_node(node.args[1]))

    return cpp.getvalue()


def codegen_if(ifcall : Call):
    assert isinstance(ifcall, Call)
    assert ifcall.func.name == "if"

    ifnode = IfNode(ifcall.func, ifcall.args)

    cpp = "if (" + codegen_node(ifnode.cond) + ") {\n"
    cpp += codegen_block(ifnode.thenblock)

    for elifcond, elifblock in ifnode.eliftuples:
        cpp += "} else if (" + codegen_node(elifcond) + ") {\n"
        cpp += codegen_block(elifblock)

    if ifnode.elseblock:
        cpp += "} else {\n"
        cpp += codegen_block(ifnode.elseblock)

    cpp += "}"

    return cpp


def codegen_block(block: Block):
    assert isinstance(block, Block)
    cpp = ""
    for b in block.args:
        cpp += codegen_node(b) + ";\n"
        # if isinstance(b, Call):
        #     if b.func.name == "if":
        #         cpp += codegen_if(b)
        # elif isinstance(b, BinOp):
        #     pass
        # elif isinstance(b, UnOp):
        #     pass
    return cpp


def indent(text, amount, ch=' '):
    return textwrap.indent(text, amount * ch)


def codegen_def(defnode: Call):
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


# class Environment:
#     def __init__(self):
#         self.parent
#         self.
