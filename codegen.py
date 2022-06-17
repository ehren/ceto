from semanticanalysis import Node, Module, Call, Block, UnOp, BinOp, ColonBinOp, Assign, NamedParameter, Identifier, IntegerLiteral, IfNode, SemanticAnalysisError

cpp_preamble = """
#include <memory>
#include <cstdio>

class object {
    virtual ~{
    };
};

"""


import io

def codegen(parsed):
    cpp = io.StringIO()
    cpp.write(cpp_preamble)



    codegen_stack = []

    #cpp.seek(io.SEEK_END)

    assert isinstance(parsed, Module) # enforced by parser
    codegen_node(parsed, cpp)

    return cpp.getvalue()


def codegen_node(node: Node, cpp):
    if isinstance(node, Module):
        for modarg in node.args:
            if modarg.func.name == "def":
                codegen_node(modarg, cpp)



def codegen_if(ifcall : Call, cpp):
    assert isinstance(ifcall, Call)
    assert ifcall.func.name == "if"

    ifnode = IfNode(ifcall.func, ifnode.args)

    # ifargs = list(ifnode.args)
    cond = ifnode.cond
    thenblock = ifnode.thenblock
    codegen_block(thenblock)

    cond = codegen_node(cond, cpp)

    cpp.write("if (")



    cpp.write("if (")


def codegen_block(block: Block, cpp):
    assert isinstance(block, Block)
    for b in block.args:
        if isinstance(b, Call):
            if b.func.name == "if":
                codegen_if(b, cpp)
        elif isinstance(b, BinOp):
            pass
        elif isinstance(b, UnOp):
            pass

        print(b)


def codegen_def(defnode: Call, cpp):
    assert defnode.func.name == "def"
    name = defnode.args[0]
    cpp.write(f"std::shared_ptr<object> {name} (")
    args = defnode.args[1:]
    block = args.pop()
    assert isinstance(block, Block)
    if len(args):
        cpp_args = ", ".join([f"std::shared_ptr<object> {a}" for a in args])
        cpp.write(cpp_args)
    cpp.write(") {\n")
    codegen_block(block, cpp)
    cpp.write("}")


# class Environment:
#     def __init__(self):
#         self.parent
#         self.
