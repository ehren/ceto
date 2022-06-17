from parser import parse
from parser import Node, Module, Call, Block, UnOp, BinOp, ColonBinOp, Assign, RedundantParens, Identifier
import io
import sys


def isa_or_wrapped(node, NodeClass):
    return isinstance(node, NodeClass) or (isinstance(node, ColonBinOp) and isinstance(node.args[0], NodeClass))


# def _monkey_ident(self, name:str):
#     self.func = name


class RebuiltIdentifer(Identifier):
    def __init__(self, name):
        self.func = name
        self.args = []
        self.name = name

# Identifier.__init__ = _monkey_ident


class RebuiltBlock(Block):

    def __init__(self, args):
        self.func = "Block"
        self.args = args


class RebuiltCall(Call):
    def __init__(self, func, args):
        self.func = func
        self.args = args



# def _monkey(self, func, args):
#     self.func = func
#     self.args = args

# Assign.__init__ = _monkey
class RebuiltAssign(Assign):
    def __init__(self, args):
        self.func = "Assign"
        self.args = args


class RebuiltColon(ColonBinOp):
    def __init__(self, func, args):
        self.func = func
        self.args = args


class NamedParameter(Node):
    def __init__(self, args):
        self.func = "NamedParameter"
        self.args = args  # [lhs, rhs]

    def __repr__(self):
        return "{}({})".format(self.func, ",".join(map(str, self.args)))


class Atom(Node):
    pass


class SemanticAnalysisError(Exception):
    pass
    #def __init__(self, message, line_number):
    #    super().__init__("{}. Line {}.".format(message, line_number))

cpp_preamble = """
#include <memory>
#include <cstdio>

class object {
    virtual ~{
    };
};

"""


def strip_types(node: Node):
    stripped = []

    def visitor(node):
        if not isinstance(node, Node):
            return node

        rebuilt = []
        if isinstance(node, ColonBinOp):
            lhs, rhs = node.args
            stripped.append(rhs)
            rebuilt.append(lhs)
        node.args = rebuilt

        rebuilt = []
        for arg in node.args:
            if isinstance(arg, Node):
                arg = visitor(arg)
            rebuilt.append(arg)
        node.args = rebuilt

    return stripped, visitor(node)


def codegen_if(ifnode, cpp):
    assert ifnode.func == "if"

    ifargs = list(ifnode.args)
    cond = ifargs.pop()

    cpp.write("if (")



    cpp.write("if (")


def codegen_block(block: Block, cpp):
    assert isinstance(block, Block)
    for b in block.args:
        if isinstance(b, Call):
            if b.func == "if":
                codegen_if(b, cpp)
        elif isinstance(b, BinOp):
            pass
        elif isinstance(b, UnOp):
            pass

        print(b)


def codegen_def(defnode: Call, cpp):
    assert defnode.func == "def"
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

def build_parents(node: Node):

    def visitor(node):
        if not isinstance(node, Node):
            return
        for arg in node.args:
            if isinstance(arg, Node):
                arg.parent = node
                visitor(arg)
    visitor(node)


def build_types(node: Node):
    stripped = []

    def visitor(node):
        if not isinstance(node, Node):
            return node

        rebuilt = []
        if isinstance(node, ColonBinOp):
            lhs, rhs = node.args
            stripped.append(rhs)
            rebuilt.append(lhs)
        node.args = rebuilt

        rebuilt = []
        for arg in node.args:
            if isinstance(arg, Node):
                arg = visitor(arg)
            rebuilt.append(arg)
        node.args = rebuilt

    return stripped, visitor(node)


def codegen_node(node: Node, cpp):
    if isinstance(node, Module):
        for modarg in node.args:
            if modarg.func == "def":
                codegen_node(modarg, cpp)




def codegen(parsed):
    cpp = io.StringIO()
    cpp.write(cpp_preamble)

    build_parents(parsed)

    codegen_stack = []

    #cpp.seek(io.SEEK_END)

    assert isinstance(parsed, Module) # enforced by parser
    codegen_node(parsed, cpp)

    return cpp.getvalue()


def one_liner_expander(parsed):

    def ifreplacer(ifop):

        if len(ifop.args) < 1:
            raise SemanticAnalysisError("not enough if args")

        if len(ifop.args) == 1 or not isinstance(ifop.args[1],
                                                 Block):
            if isinstance(ifop.args[0], ColonBinOp):
                # convert second arg of outermost colon to one element block
                rebuilt = [ifop.args[0].args[0], RebuiltBlock(
                    args=[ifop.args[0].args[1]])] + ifop.args[1:]
                return RebuiltCall(func="if", args=rebuilt)
            else:
                raise SemanticAnalysisError("bad first if-args")

        for i, a in enumerate(list(ifop.args[2:]), start=2):
            if isinstance(a, Block):
                if not ifop.args[i - 1] == "else" and (not isinstance(ifop.args[i - 1], ColonBinOp) or ifop.args[i - 1].args[0] != "elif"):
                    raise SemanticAnalysisError(
                        f"Unexpected if arg. Found block at position {i} but it's not preceded by 'if' or 'elif'")
            elif isinstance(a, ColonBinOp):
                if not a.args[0] in ["elif", "else"]:
                    raise SemanticAnalysisError(
                        f"Unexpected if arg {a} at position {i}")
                if a.args[0] == "else":
                    rebuilt = ifop.args[0:i] + [a.args[0], RebuiltBlock(
                        args=[a.args[1]])] + ifop.args[i + 1:]
                    return RebuiltCall(ifop.func, args=rebuilt)
                elif a.args[0] == "elif":
                    if i == len(ifop.args) - 1 or not isinstance(ifop.args[i + 1], Block):
                        c = a.args[1]
                        if not isinstance(c, ColonBinOp):
                            raise SemanticAnalysisError("bad if args")
                        cond, rest = c.args
                        new_elif = RebuiltColon(a.func, [a.args[0], cond])
                        new_block = RebuiltBlock(args=[rest])
                        rebuilt = ifop.args[0:i] + [new_elif, new_block] + ifop.args[i + 1:]
                        return RebuiltCall(ifop.func, args=rebuilt)
            elif a == "else":
                if not i == len(ifop.args) - 2:
                    raise SemanticAnalysisError("bad else placement")
                if not isinstance(ifop.args[-1], Block):
                    raise SemanticAnalysisError("bad arg after else")
            else:
                raise SemanticAnalysisError(
                    f"bad if-arg {a} at position {i}")

        return ifop

    def visitor(op):

        if not isinstance(op, Node):
            return False, op

        if isinstance(op, Call):
            if op.func == "def":
                if len(op.args) < 2:
                    raise SemanticAnalysisError("not enough def args")
                if not isinstance(op.args[0], str):
                    raise SemanticAnalysisError("bad def args (first arg must be an identifier)")
                if not isinstance(op.args[-1], Block):
                    # last arg becomes one-element block
                    return True, RebuiltCall(func=op.func, args=op.args[0:-1] + [RebuiltBlock(args=[op.args[-1]])])
            elif op.func == "if":
                new = ifreplacer(op)
                if new is not op:
                    return True, new

        rebuilt = []
        changed = False

        for arg in op.args:
            arg_change, arg = visitor(arg)
            if arg_change:
                changed = True
            rebuilt.append(arg)

        if changed:
            op.args = rebuilt

        return changed, op

    while True:
        did_change, parsed = visitor(parsed)
        if not did_change:
            break

    return parsed


def assign_to_named_parameter(parsed):

    def replacer(op):
        if not isinstance(op, Node):
            return op
        if isinstance(op, Call):
            rebuilt = []
            for arg in op.args:
                if isinstance(arg, ColonBinOp):
                    if isinstance(arg.args[0], Assign):
                        rebuilt.append(RebuiltColon(func=arg.func, args=[NamedParameter(args=arg.args[0].args), arg.args[1]]))
                    else:
                        rebuilt.append(arg)
                elif isinstance(arg, Assign):
                    rebuilt.append(NamedParameter(args=arg.args))
                elif isinstance(arg, RedundantParens) and isa_or_wrapped(arg.args[0], Assign):
                    rebuilt.append(arg.args[0])
                else:
                    rebuilt.append(arg)
            op.args = rebuilt

        op.args = [replacer(arg) for arg in op.args]
        return op

    return replacer(parsed)


def warn_and_remove_redundant_parens(expr, error=False):

    def replacer(op):
        if isinstance(op, RedundantParens):
            op = op.args[0]
            msg = f"warning: redundant parens {op}"
            if error:
                raise SemanticAnalysisError(msg)
            else:
                print(msg, file=sys.stderr)
        if not isinstance(op, Node):
            return op
        op.args = [replacer(arg) for arg in op.args]
        return op

    return replacer(expr)


def semantic_analysis(parsed: Module):
    assert isinstance(parsed, Module) # enforced by parser

    for modarg in parsed.args:
        if isinstance(modarg, Call):
            if modarg.func.name not in ["def", "class"]:
                raise SemanticAnalysisError("Only defs or classes at module level (for now)")
        elif isinstance(modarg, Assign):
            pass
        else:
            raise SemanticAnalysisError("Only calls and assignments at module level (for now)")

    parsed = one_liner_expander(parsed)
    parsed = assign_to_named_parameter(parsed)
    parsed = warn_and_remove_redundant_parens(parsed)
    return parsed


def compile(s):
    parsed = parse(s)
    parsed = semantic_analysis(parsed)
    print("semantic", parsed)
    code = codegen(parsed)
    print("code:\n", code)


if __name__ == "__main__":
    compile("""
def (main:
    foo((x=y:int:strong), x=y:int:weak)
    foo(x=y:int, (z=y:int))
    (1+1)
)
    """)

    0 and compile("""
def (main:
    # if (1:1)
    if (if(1:1):1)
    # def (x,1)
    # if (1: 1, elif: x: 2, else: 0)
    # if (elif:x:int:5:int) # should result in "unknown identifier 'elif'"
    if ((x:int):0:int, elif:(x:int):5:int)  # works
    # if (x:int:y=0:int,elif:x:int:5:int, else:x=2:int) # nonsense but lowered correctly
    # if ((x:int):y=0:int,elif:(x:int):5:int, else:x=2:int) # correct
    # y=((x=123456789))
)""")

    0 and compile("""
def (bar, x, y, 0)
def (foo, x, y:
    # parser: [Module([def(['bar', 'x', 'y', 0]), def(['foo', 'x', 'y', Block([[if([:(x,int), :(1,int), :(elif,:(-(x,1),int)), :(5,int), :(else,:(0,int))])], 
    #[if([:(1,1), 
    # :(elif,:(:(x,int),:(5,int))), 
    # :(else,:(0,int))])]])])])]

    #if (x:int, 1:int, elif:x-1:int, 5:int, else: 0:int)
    #[if([:(1,1), 
    # :(elif, :(x,:(int,:(5,int)))), 
    # :(else,0)])]
    #if (1:1, elif:x:int:5:int, else: 0:int)
    if (1:1)
    if (elif:x:int:5:int) # should result in "unknown identifier 'int'"
    if (elif:(x:int):5:int)
    #if (1:1, elif:(x:int):5:int, else: 0:int)
    #if (1:1, elif:x:5, else: 0)
)""")

    0 and compile("""
def (bar, x, y, 0)
def (foo, x, y:
    if (1:
        print("1")
        2
    )

    if (2:
        5
    elif: y: 2, else: 0)

    if (x:int, 5:int, elif: x = y : int, 0, else: 0)
    if (x:int, 1, elif:x-1:int, 5, else: 0)
    if (x:int, 1:int, elif:x-1:int, 5:int, else: 0:int)
    #if (x:int, 1, elif:x+1: 0:int)  # invalid if semantics
    if (x:int, 1, elif:x+1, 0:int, else: 5)
    if (x, 1, elif: y, 2)
    x=if (x, 1)
    lambda (x, y, z:int, 0)
    lambda (x:int, y:int, z:int:
        0
    )
    lambda(1)
    lambda(:
        1
    )
    lambda(x:int:
        1
    )
    lambda(x:int, 1)
)

    """)


    0 and compile("""
if (x: 
    y
    x+1
    3
    z = 5+4
)
foo(x,y)
foo(x,y)""")
