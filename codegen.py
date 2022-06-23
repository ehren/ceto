from semanticanalysis import Node, Module, Call, Block, UnOp, BinOp, ColonBinOp, Assign, NamedParameter, Identifier, IntegerLiteral, IfNode, SemanticAnalysisError, SyntaxColonBinOp
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


# Uses code and ideas from https://github.com/lukasmartinelli/py14

# https://brevzin.github.io/c++/2019/12/02/named-arguments/


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
    name = defnode.args[0].name
    args = defnode.args[1:]
    block = args.pop()
    assert isinstance(block, Block)

    params = []
    for idx, arg in enumerate(args):
        params.append(("T" + str(idx + 1), arg.name))
    typenames = ["typename " + arg[0] for arg in params]

    template = "inline "
    if name == "main":
        template = ""
    if typenames:
        template = "template <{0}>\n".format(", ".join(typenames))
    params = ["{0} {1}".format(arg[0], arg[1]) for arg in params]

    return_type = "auto"
    if name == "main":
        return_type = "int"

    funcdef = "{0}{1} {2}({3})".format(template, return_type, name,
                                       ", ".join(params))
    return funcdef + " {\n" + codegen_block(block) + "\n}"


def codegen_lambda(node):
    args = list(node.args)
    block = args.pop()
    assert isinstance(block, Block)
    params = ["auto {0}".format(param.name) for param in args]
    funcdef = "auto {0} = []({1})".format(node.name, ", ".join(params))
    return funcdef + " {\n" + codegen_block(block) + "\n};"



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
        else:
            pass

    elif isinstance(node, (Identifier, IntegerLiteral)):
        cpp.write(str(node))
    # elif isinstance(node, UnOp):
        # if node.func == "return":  # TODO fix UnOp func should be an identifier (although UnOp return should be converted to ColonBinOp earlier - or removed from language)
        #     cpp.write("return")
    elif isinstance(node, BinOp):
        if isinstance(node, ColonBinOp):
            assert isinstance(node, SyntaxColonBinOp)  # sanity check type system isn't leaking
            if node.args[0].name == "return":
                cpp.write("return " + codegen_node(node.args[1]))
            else:
                assert False
        else:
            cpp.write(codegen_node(node.args[0]) + node.func + codegen_node(node.args[1]))

    return cpp.getvalue()
