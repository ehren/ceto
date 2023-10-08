import typing

selfhost = True
try:
    # from ._abstractsyntaxtree import *
    selfhost = False
except ImportError:
    selfhost = False
    # raise  # comment this out to use pure python ast

if not selfhost:
    # TODO should throw away the ladder soon

    class Node:

        def __init__(self, func, args, source = None):
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
        def __init__(self, op, args, source=None):
            self.op = op
            super().__init__(None, args, source)

        def __repr__(self):
            return "({} {})".format(self.op, self.args[0])


    class LeftAssociativeUnOp(Node):
        def __init__(self, op, args, source=None):
            self.op = op
            super().__init__(None, args, source)

        def __repr__(self):
            return "({} {})".format(self.args[0], self.op)


    class BinOp(Node):
        def __init__(self, op, args, source=None):
            self.op = op
            super().__init__(None, args, source)

        def __repr__(self):
            return "({} {} {})".format(self.lhs, self.op, self.rhs)

        @property
        def lhs(self):
            return self.args[0]

        @property
        def rhs(self):
            return self.args[1]


    class TypeOp(BinOp):
        pass


    class SyntaxTypeOp(TypeOp):
        def __init__(self, op, args, source=None):
            self.synthetic_lambda_return_lambda = None
            super().__init__(op, args, source)


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
        def __init__(self, name, source = None):
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
            escaped = self.str.replace("\n", r"\n")
            escaped = escaped.replace('"', r'\"')
            escaped = '"' + escaped + '"'
            return escaped

        def __init__(self, string, prefix=None, suffix=None, source=None):
            self.str = string
            self.prefix = prefix
            self.suffix = suffix
            super().__init__(None, [], source)


    class IntegerLiteral(Node):
        def __init__(self, integer_string, suffix=None, source=None):
            self.integer_string = integer_string
            self.suffix = suffix
            super().__init__(None, [], source)

        def __repr__(self):
            # return str(self.integer) + self.suffix.name if self.suffix else ""  # oops wrong precedence for ternary if
            return self.integer_string + (self.suffix.name if self.suffix else "")


    class FloatLiteral(Node):
        def __init__(self, float_string : str, suffix=None, source=None):
            self.float_string = float_string
            self.suffix = suffix
            super().__init__(None, [], source)

        def __repr__(self):
            return self.float_string + (self.suffix.name if self.suffix else "")


    class ListLike_(Node):
        def __init__(self, args, source=None):
            super().__init__(func=None, args=args, source=source)

        def __repr__(self):
            return "{}({})".format(self.__class__.__name__, ",".join(map(str, self.args)))


    class ListLiteral(ListLike_):
        pass


    class TupleLiteral(ListLike_):
        pass


    class BracedLiteral(ListLike_):
        pass


    class Block(ListLike_):
        pass


    class Module(Block):
        def __init__(self, args, source=None):
            self.has_main_function = False
            super().__init__(args, source)


    class NamedParameter(Assign):
        # def __init__(self, args):
        #     # self.func = "NamedParameter"
        #     func = "="  # paper over that we've further loosened named parameter vs assignment distinction in codegen
        #     super(Node).__init__(func, args, None)

        def __repr__(self):
            return "{}({})".format("NamedParameter",
                                   ",".join(map(str, self.args)))

    class RedundantParens(Node):
        def __init__(self, args, source=None):
            self.args = args
            super().__init__(None, self.args, source)

        def __repr__(self):
            return "{}({})".format("RedundantParens", ",".join(map(str, self.args)))


    # this introduces an implicit wrapper node around every infix expression
    # but it allows us to preserve truly redundant parentheses by checking for
    # double wrapped nodes. (e.g. assignment expression instead of named parameter
    # in call requires one set extra parens)
    class InfixWrapper_(Node):
        def __init__(self, args, source=None):
            self.args = args
            super().__init__(None, self.args, source)

        def __repr__(self):
            return "{}({})".format("InfixWrapper_", ",".join(map(str, self.args)))

