class Node:

    def __init__(self, func, args, source):
        self.name = None
        self.parent = None
        self.declared_type = None
        self.func = func
        self.args = args
        self.source = source

    def __repr__(self):
        return "{}({})({!r})".format(self.__class__.__name__,
                                     self.func, self.args)


class UnOp(Node):
    pass


class LeftAssociativeUnOp(Node):
    pass


class BinOp(Node):

    def __repr__(self):
        return "({} {} {})".format(self.lhs, self.func, self.rhs)

    @property
    def lhs(self):
        return self.args[0]

    @property
    def rhs(self):
        return self.args[1]


class TypeOp(BinOp):
    pass


class SyntaxTypeOp(TypeOp):
    pass


class AttributeAccess(BinOp):

    def __repr__(self):
        return "{}.{}".format(self.lhs, self.rhs)


class ArrowOp(BinOp):
    pass


class ScopeResolution(BinOp):
    pass


class Assign(BinOp):
    pass


class Call(Node):
    def __repr__(self):
        return "{}({})".format(self.func, ",".join(map(str, self.args)))


class ArrayAccess(Node):
    def __repr__(self):
        return "{}[{}]".format(self.func, ",".join(map(str, self.args)))


class BracedCall(Node):
    def __repr__(self):
        return "{}[{}]".format(self.func, ",".join(map(str, self.args)))


class Template(Node):
    # template-id in proper standardese
    def __repr__(self):
        return "{}<{}>".format(self.func, ",".join(map(str, self.args)))


class Identifier(Node):
    def __init__(self, name, source):
        super().__init__(None, [], source)
        self.name = name

    def __repr__(self):
        return self.name


class StringLiteral(Node):

    def __repr__(self):
        escaped = self.func.replace("\n", r"\n")
        return '"' + escaped + '"'


class CStringLiteral(StringLiteral):
    pass


class IntegerLiteral(Node):
    def __init__(self, integer, source):
        func = None
        args = []
        self.integer = integer
        super().__init__(None, args, source)

    def __repr__(self):
        return str(self.integer)


class _ListLike(Node):
    def __repr__(self):
        return "{}({})".format(self.func, ",".join(map(str, self.args)))


class ListLiteral(_ListLike):
    pass


class TupleLiteral(_ListLike):
    pass


class BracedLiteral(_ListLike):
    pass


class Block(_ListLike):

    def __init__(self, args):
        super().__init__(func=self.__class__.__name__, args=args, source=None)


class Module(Block):
    def __init__(self, args):
        self.has_main_function = False
        super().__init__(args)


class RedundantParens(Node):
    def __init__(self, args):
        self.func = "RedundantParens"
        self.args = args
        super().__init__(self.func,self.args,None)


