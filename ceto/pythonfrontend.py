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
        deco_names = []
        template_str = ""

        # Check for native Python generic parameters (3.12+)
        if hasattr(node, 'type_params') and node.type_params:
            params = [self.visit(p) for p in node.type_params]
            template_str = "<" + ", ".join(params) + ">"

        if node.decorator_list:
            for decorator in node.decorator_list:

                if isinstance(decorator, ast.Name):
                    deco_names.append(decorator.id)
                elif isinstance(decorator, ast.Call):
                    deco_names.append(self.visit(decorator))

        # Apply decorator suffixes as "type of the name of the def"

        name_suffix = ":" + ":".join(deco_names) if deco_names else ""

        s = "def (" + node.name + template_str + name_suffix

        args_str = self.visit(node.args)
        if args_str.strip():
            s += ", " + args_str

        s += ":\n"
        s += self.handle_visit_block(node.body)
        s += self.cx.indent*"    " + ")"

        if node.returns:
            s += " : " + self.visit(node.returns)

        return s

    def visit_ClassDef(self, node: ast.ClassDef):
        keyword = "class"
        other_decorators = []
        template_str = ""

        # Check for native Python generic parameters (3.12+)
        if hasattr(node, 'type_params') and node.type_params:
            params = [self.visit(p) for p in node.type_params]
            template_str = "<" + ", ".join(params) + ">"

        if node.decorator_list:
            for decorator in node.decorator_list:

                if isinstance(decorator, ast.Name):
                    if decorator.id == "struct":
                        keyword = "struct"
                    else:
                        other_decorators.append(decorator.id)

                elif isinstance(decorator, ast.Call):
                    other_decorators.append(self.visit(decorator))


        s = keyword + " (" + node.name + template_str

        if node.bases:
            bases_str = ", ".join([self.visit(b) for b in node.bases])
            s += "(" + bases_str + ")"

        s += ":\n"
        s += self.handle_visit_block(node.body)
        s += self.cx.indent*"    " + ")"

        # Add remaining decorators as a type suffix
        suffix = ""
        if other_decorators:
            suffix = " : " + ":".join(other_decorators)

        return s + suffix


    def visit_If(self, node: ast.If):
        s = "if (" + self.visit(node.test) + ":\n"
        s += self.handle_visit_block(node.body)

        orelse = node.orelse
        while orelse:
            if isinstance(orelse[0], ast.If):
                s += self.cx.indent*"    " + "elif " + self.visit(orelse[0].test) + ":\n"
                s += self.handle_visit_block(orelse[0].body)
                orelse = orelse[0].orelse
            else:
                s += self.cx.indent*"    " + "else:\n"
                s += self.handle_visit_block(orelse)
                break

        s += self.cx.indent*"    " + ")"
        return s

    def visit_While(self, node: ast.While):
        s = "while (" + self.visit(node.test) + ":\n"
        s += self.handle_visit_block(node.body)
        s += self.cx.indent*"    " + ")"
        return s

    def visit_For(self, node: ast.For):
        s = "for (" + self.visit(node.target) + " in " + self.visit(node.iter) + ":\n"
        s += self.handle_visit_block(node.body)
        s += self.cx.indent*"    " + ")"
        return s

    def visit_Lambda(self, node: ast.Lambda):
        # uses one-liner lambda with non-block param (no multi-line lambdas in python)
        s = "lambda ("
        args_str = self.visit(node.args)
        s += args_str + ", "
        s += self.visit(node.body)
        s += ")"
        return s


if __name__ == "__main__":
    expr = r"""
@blah
@bleh
@struct
@blech
class MyDecoratedStruct:
    x
    y: int

@static
@inline
def get_count() -> int:
    return 5
"""

    a = ast.parse(expr)
    v = Visitor()
    out = v.visit(a)
    print(out)
