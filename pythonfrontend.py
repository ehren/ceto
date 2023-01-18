import ast
import typing


class Context:
    indent = 0


class Visitor(ast.NodeVisitor):

    def __init__(self):
        self.cx = Context()

    def generic_visit(self, node):
        return ast.unparse(node)

    def handle_visit_block(self, block):
        self.cx.indent += 1
        s = ""
        for b in block:
            s += self.cx.indent*"    " + self.visit(b) + "\n"
        self.cx.indent -= 1
        return s

    def visit_Module(self, node: ast.Module):
        s = ""
        for c in ast.iter_child_nodes(node):
            s += self.visit(c) + "\n"
        return s

    def visit_FunctionDef(self, node: ast.FunctionDef):
        s = "def (" + node.name

        # this is fine for now (relies on default visit_arguments/generic_visit)
        # but may need adjusting for keyword only args etc etc
        args_str = self.visit(node.args)
        if args_str.strip():
            s += ", " + args_str

        s += ":\n"

        s += self.handle_visit_block(node.body)

        s += self.cx.indent*"    " + ")"

        if node.returns:
            s += " : " + self.visit(node.returns)

        return s

    def visit_If(self, node: ast.If):
        s = "if (" + self.visit(node.test) + ":\n"

        s += self.handle_visit_block(node.body)

        orelse = node.orelse

        while orelse:

            if isinstance(orelse[0], ast.If):
                # elif
                s += self.cx.indent*"    " + "elif " + self.visit(orelse[0].test) + ":\n"
                s += self.handle_visit_block(orelse[0].body)
                orelse = orelse[0].orelse
            else:
                # else
                s += self.cx.indent*"    " + "else:\n"
                s += self.handle_visit_block(orelse)
                break

        s += self.cx.indent*"    " + ")"
        return s

    def visit_For(self, node: ast.For):
        s = "for (" + self.visit(node.target) + " in " + self.visit(node.iter) + ":\n"
        s += self.handle_visit_block(node.body)
        s += self.cx.indent*"    " + ")"
        return s


if __name__ == "__main__":
    expr = r"""
# def main(argc: int, argv: ptr(ptr(char))) -> int:      # this interferes with planned function ptr syntax
# def main(argc: const.int, argv: char.ptr.ptr) -> int:  # too confusing? also clashes with attribute access scope resolution e.g. std.vector)
# def main(argc: int, argv: char+ptr+ptr) -> int:        # this is also problematic e.g. explicit non-type template parameters (although no template syntax in python anyway)
# def main(argc: int, argv: "char**") -> int:         # problematic for same reasons
def main(argc: types("const int"), argv: types(char,ptr,ptr)) -> int:  # allow string or list. would also allow: template(std.vector, types(int,ptr))
    x:int = 5

    if x == 0:
        y = 1
    elif x == 1:
        y = 2
    elif x == 1:
        y = 2
        y = 4
    elif x == 1:
        y = 2
        for i in [0,1,2]:
            std.cout << i
    else:
        y = 3
        y = 5
    std.cout << y
    
    """
    a = ast.parse(expr)
    v = Visitor()
    out = v.visit(a)
    print(out)

