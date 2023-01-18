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
        s = self.cx.indent*"    " + "def (" + node.name

        if node.args.args:
            # TODO default arguments etc
            s += ", " + ", ".join(self.visit(node.args.args))

        s += ":\n"

        s += self.handle_visit_block(node.body)

        s += self.cx.indent*"    " + ")"

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
def main():
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

