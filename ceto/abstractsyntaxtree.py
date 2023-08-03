import typing


class Node:

    def __init__(self, func, args, source):
        self.name : str = None
        self.parent : Node = None
        self.declared_type : Node = None
        self.scope = None
        self.func : Node = func
        self.args : typing.List[Node] = args
        self.source : typing.Tuple[str, int] = source

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
        return str(self.func) + "{" + ",".join(map(str, self.args)) + "}"


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
        escaped = self.escaped()
        if self.prefix:
            escaped = self.prefix.name + escaped
        if self.suffix:
            escaped += self.suffix.name
        return escaped

    def escaped(self):
        escaped = self.string.replace("\n", r"\n")
        escaped = '"' + escaped + '"'
        return escaped

    def __init__(self, string, prefix, suffix, source):
        self.string = string
        self.prefix = prefix
        self.suffix = suffix
        super().__init__(None, [], source)


class IntegerLiteral(Node):
    def __init__(self, integer, source):
        self.integer = integer
        super().__init__(None, [], source)

    def __repr__(self):
        return str(self.integer)


class _ListLike(Node):
    def __init__(self, args, source):
        super().__init__(func=None, args=args, source=source)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ",".join(map(str, self.args)))


class ListLiteral(_ListLike):
    pass


class TupleLiteral(_ListLike):
    pass


class BracedLiteral(_ListLike):
    pass


class Block(_ListLike):
    def __init__(self, args, source=None):
        super().__init__(args, source)


class Module(Block):
    def __init__(self, args, source):
        self.has_main_function = False
        super().__init__(args, source)


class RedundantParens(Node):
    def __init__(self, args):
        self.func = "RedundantParens"
        self.args = args
        super().__init__(self.func,self.args,None)


