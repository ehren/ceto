#
# Based on the pyparsing examples: parsePythonValue.py, left_recursion.py, simpleBool.py
#
# 
#
import pyparsing as pp

import io

from preprocessor import preprocess


class Node:

    @property
    def name(self):
        if not hasattr(self, "_name"):
            self._name = None
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    @property
    def parent(self):
        if not hasattr(self, "_parent"):
            self._parent = None
        return self._parent

    @parent.setter
    def parent(self, n):
        self._parent = n

    @property
    def declared_type(self):
        if not hasattr(self, "_declared_type"):
            self._declared_type = None
        return self._declared_type

    @declared_type.setter
    def declared_type(self, t):
        self._declared_type = t


    def __repr__(self):
        return "{}({})({!r})".format(self.__class__.__name__,
                                     self.func, self.args)


class UnOp(Node):
    def __init__(self, tokens):
        self.func = tokens[0][0]
        self.args = [tokens[0][1]]


class BinOp(Node):
    def __init__(self, tokens):
        self.args = tokens[0][::2]
        self.func = tokens[0][1]

    def __repr__(self):
        return "({} {} {})".format(self.lhs, self.func, self.rhs)

    @property
    def lhs(self):
        return self.args[0]

    @property
    def rhs(self):
        return self.args[1]


class _LeftAssociativeBinOp(BinOp):

    def __init__(self, tokens):
        self.func = tokens[0][1]

        first_arg = tokens[0][0]
        rest = tokens[0][2:]

        if len(rest) > 1:
            others = [rest[0], self.func] + rest[2:]
            self.args = [first_arg, _LeftAssociativeBinOp(pp.ParseResults([others]))]
        else:
            self.args = [first_arg, rest[0]]

        # self.args = tokens[0][::2]
        # self.args = [tokens[0][0], tokens[0][1:]]
        # print("binop args", self.args)


# https://stackoverflow.com/questions/4571441/recursive-expressions-with-pyparsing/4589920#4589920
# parse action -maker
def make_LR_like(numterms, AstClass):
    if numterms is None:
        # None operator can only by binary op
        initlen = 2
        incr = 1
    else:
        initlen = {0:1,1:2,2:3,3:5}[numterms]
        incr = {0:1,1:1,2:2,3:4}[numterms]

    # define parse action for this number of terms,
    # to convert flat list of tokens into nested list
    def pa(s,l,t):
        t = t[0]
        if len(t) > initlen:
            # ret = pp.ParseResults(t[:initlen])
            ret = AstClass(t[:initlen])
            i = initlen
            while i < len(t):
                # ret = pp.ParseResults([ret] + t[i:i+incr])
                ret = AstClass([ret] + t[i:i+incr])
                i += incr
            # return pp.ParseResults([ret])
            return AstClass([ret])
    return pa



class ColonBinOp(BinOp):
    def __init__(self, tokens):
        super().__init__(tokens)
        if self.func == "as":
            self.args = list(reversed(self.args))
            self.func = ":"


class RebuiltColon(ColonBinOp):
    def __init__(self, func, args, _is_as_hack=False):
        self.func = func
        self.args = args
        self._is_as_hack = _is_as_hack


class SyntaxColonBinOp(ColonBinOp):
    def __init__(self, func, args):
        self.func = func
        self.args = args


# class AttributeAccess(_LeftAssociativeBinOp):
class AttributeAccess(BinOp):

    def __repr__(self):
        return "{}.{}".format(self.lhs, self.rhs)

    def __init__(self, tokens):
        super().__init__(tokens)


class AsOp(BinOp):
    pass
    # def __init__(self, func, args):
    #     self.func = func
    #     self.args = args


class Assign(BinOp):
    pass
    # def __init__(self, s, loc, tokens):
    #     print("assign", loc, tokens)
    #     super().__init__(tokens)


# this introduces an implicit wrapper node around every infix expression
# but it allows us to preserve truly redundant parentheses by checking for
# double wrapped nodes. (e.g. assignment expression instead of named parameter
# in call requires one set extra parens)
class _InfixExpr(Node):
    def __init__(self, t):
        self.func = "_InfixExpr"
        self.args = [t.as_list()[0]]

    def __repr__(self):
        return "{}({})".format(self.func, ",".join(map(str, self.args)))


# Note: This is not created by the parser (later used to signify non-named parameters)
class RedundantParens(Node):
    def __init__(self, args):
        self.func = "RedundantParens"
        self.args = args


class Call(Node):
    def __repr__(self):
        return "{}({})".format(self.func, ",".join(map(str, self.args)))

    def __init__(self, tokens):
        self.func = tokens[0]
        self.args = tokens.as_list()[1:]


class ArrayAccess(Node):
    def __repr__(self):
        return "{}[{}]".format(self.func, ",".join(map(str, self.args)))

    def __init__(self, tokens):
        self.func = tokens[0]
        self.args = tokens.as_list()[1:]


class Identifier(Node):
    def __init__(self, token):
        self.func = str(token[0])
        self.name = self.func
        self.args = []

    def __repr__(self):
        return str(self.func)


class StringLiteral(Node):
    def __init__(self, token):
        self.func = str(token[0])
        self.name = None
        self.args = []

    def __repr__(self):
        # escaped = self.func.translate(str.maketrans({"\n": r"\n" }))
        escaped = self.func.replace("\n", r"\n")

        return '"' + escaped + '"'


class CStringLiteral(StringLiteral):
    def __init__(self, token):
        self.func = str(token[0])
        self.name = None
        self.args = []


class RebuiltStringLiteral(StringLiteral):
    def __init__(self, s):
        self.func = s
        self.name = None
        self.args = []

    def __repr__(self):
        # escaped = self.func.translate(str.maketrans({"\n": r"\n" }))
        escaped = self.func.replace("\n", r"\n")

        return '"' + escaped + '"'


class IntegerLiteral(Node):
    def __init__(self, token):
        self.func = int(token[0])
        self.args = []

    def __repr__(self):
        return str(self.func)


class _ListLike(Node):
    def __repr__(self):
        return "{}({})".format(self.func, ",".join(map(str, self.args)))

    def __init__(self, tokens):
        self.args = tokens.as_list()


class ListLiteral(_ListLike):

    def __init__(self, tokens):
        super().__init__(tokens)
        self.func = "List"


class TupleLiteral(_ListLike):

    def __init__(self, tokens):
        super().__init__(tokens)
        self.func = "Tuple"


class Block(_ListLike):

    def __init__(self, tokens):
        super().__init__(tokens)
        self.func = "Block"


class Module(Block):
    def __init__(self, tokens):
        super().__init__(tokens)
        self.func = "Module"


import sys
sys.setrecursionlimit(10000)

pp.ParserElement.enable_left_recursion()


def _create():


    cvtReal = lambda toks: float(toks[0])

    # define punctuation as suppressed literals
    lparen, rparen, lbrack, rbrack, lbrace, rbrace, comma = map(
        pp.Suppress, "()[]{},"
    )

    integer = pp.Regex(r"[+-]?\d+").setName("integer").set_parse_action(IntegerLiteral)
    real = pp.Regex(r"[+-]?\d+\.\d*([Ee][+-]?\d+)?").setName("real").set_parse_action(cvtReal)
    tuple_literal = pp.Forward()
    list_literal = pp.Forward()
    dictStr = pp.Forward()
    function_call = pp.Forward()
    array_access = pp.Forward()
    infix_expr = pp.Forward()
    ident = pp.Word(pp.alphas + "_", pp.alphanums + "_").set_parse_action(Identifier)

    quoted_str = pp.QuotedString("'", multiline=True).set_parse_action(StringLiteral)
    dblquoted_str = pp.QuotedString('"', multiline=True).set_parse_action(StringLiteral)
    cdblquoted_str = pp.Suppress(pp.Keyword("c")) + pp.QuotedString('"', multiline=True).set_parse_action(CStringLiteral)

    expr = (
        function_call
        | array_access
        | real
        | integer
        | cdblquoted_str
        | quoted_str
        | dblquoted_str
        | list_literal
        | tuple_literal
        | dictStr
        | ident
    )

    expop = pp.Literal("^")
    signop = pp.oneOf("+ -")
    multop = pp.oneOf("* /")
    plusop = pp.oneOf("+ -")
    colon = pp.Literal(":")
    dot = pp.Literal(".")


    _compar_atoms = list(map(pp.Literal, ["<", "<=",  ">",  ">=", "!=", "=="]))
    _compar_atoms.extend(map(pp.Keyword, ["in", "not in", "is", "is not"]))
    comparisons = _compar_atoms.pop()
    for c in _compar_atoms:
        comparisons |= c

    infix_expr <<= pp.infix_notation(
        expr,
        [
            (dot, 2, pp.opAssoc.LEFT, AttributeAccess),
            (expop, 2, pp.opAssoc.RIGHT, BinOp),
            (signop, 1, pp.opAssoc.RIGHT, UnOp),
            (multop, 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            # (plusop, 2, pp.opAssoc.LEFT, make_LR_like(2, BinOp)),
            (plusop, 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            ((pp.Literal("<<")|pp.Literal(">>")), 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            # ((pp.Keyword("left_shift")|pp.Keyword("right_shift")), 2, pp.opAssoc.LEFT, BinOp),
            (comparisons, 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (pp.Keyword("not"), 1, pp.opAssoc.RIGHT, UnOp),
            (pp.Keyword("and"), 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (pp.Keyword("or"), 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            ("=", 2, pp.opAssoc.RIGHT, Assign),
            (pp.Keyword("return"), 1, pp.opAssoc.RIGHT, UnOp),
            (colon, 1, pp.opAssoc.RIGHT, UnOp),  # unary : shold bind less tight than binary
            ((colon | pp.Keyword("as")), 2, pp.opAssoc.RIGHT, ColonBinOp),
            # (pp.Keyword("as"), 2, pp.opAssoc.LEFT, ColonBinOp),
            # (colon, 2, pp.opAssoc.RIGHT, ColonBinOp),
        ],
        # pp.Literal("("),
        # pp.Literal(")")
    ).set_parse_action(_InfixExpr)

    # plusop.add_parse_action(BinOp)

    tuple_literal <<= (
        # lparen + pp.Optional(pp.delimitedList(infix_expr)) + pp.Optional(comma) + rparen
        # lparen + pp.delimitedList(infix_expr) + pp.Optional(comma) + rparen
        (lparen + pp.delimited_list(infix_expr, min=2, allow_trailing_delim=True) + rparen) |
        (lparen + pp.Optional(infix_expr) + comma + rparen) |
        (lparen + rparen)
    ).set_parse_action(TupleLiteral)

    list_literal <<= (
        lbrack + pp.Optional(pp.delimitedList(infix_expr) + pp.Optional(comma)) + rbrack
    ).set_parse_action(ListLiteral)

    bel = pp.Suppress('\x07')

    dictEntry = pp.Group(infix_expr + bel + infix_expr)
    dictStr <<= (
        lbrace + pp.Optional(pp.delimitedList(dictEntry) + pp.Optional(comma)) + rbrace
    )

    block_line_end = pp.Suppress(";")
    # block_line_end could be OneOrMore but let's only allow semicolon separators not terminators:
    block = bel + pp.OneOrMore(infix_expr + block_line_end).set_parse_action(Block)

    array_access <<= ((expr | (lparen + infix_expr + rparen)) + lbrack + infix_expr + pp.Optional(bel + infix_expr) + pp.Optional(bel + infix_expr) + rbrack).set_parse_action(ArrayAccess)

    function_call <<= ((expr | (lparen + infix_expr + rparen)) + lparen + pp.Optional(pp.delimitedList(pp.Optional(infix_expr))) + pp.ZeroOrMore(block + pp.Optional(pp.delimitedList(pp.Optional(infix_expr)))) + rparen).set_parse_action(Call)

    module = pp.OneOrMore(infix_expr + block_line_end).set_parse_action(Module)
    return module

grammar = _create()


def parse(s):
    print(s)
    # transformed = io.StringIO(s)
    pp.ParserElement.set_default_whitespace_chars(" \t\n")

    filter_comments = pp.Regex(r"#.*")
    filter_comments = filter_comments.suppress()
    qs = pp.QuotedString('"') | pp.QuotedString("'")
    filter_comments = filter_comments.ignore(qs)

    transformed = s

    transformed = filter_comments.transform_string(transformed)

    pp.ParserElement.set_default_whitespace_chars(" \t")

    # patterns = [(pp.Keyword(k) + ~pp.FollowedBy(pp.Literal(":") | pp.Literal("\n"))) for k in ["elif", "else", "except"]]
    patterns = [(pp.Keyword(k) + ~pp.FollowedBy(pp.Literal(":") | pp.Literal("\n"))) for k in ["elif", "except"]]
    # patterns += [(pp.Keyword(k) + ~pp.FollowedBy(pp.Literal(":") | pp.Literal("\n") | pp.Literal(")"))) for k in ["return"]]
    # patterns += [(pp.Keyword(k) + ~pp.FollowedBy(pp.Literal("\n"))) for k in ["except"]]
    pattern = None
    for p in patterns:
        p = p.set_parse_action(lambda t: t[0] + ":")
        if pattern is None:
            pattern = p
        pattern |= p
    # transformed = pattern.set_parse_action(lambda t: t[0] + ":")# .ignore(qs).transform_string(transformed)


    # transformed = pattern pattern.set_parse_action(lambda t: t[0] + ":")# .ignore(qs).transform_string(transformed)
    transformed = pattern.transform_string(transformed)

    patterns = [pp.Keyword(k) for k in ["elif", "else", "except"]]
    pattern = None
    for p in patterns:
        p = p.set_parse_action(lambda t: "," + t[0])
        if pattern is None:
            pattern = p
        pattern |= p

    pattern = pattern.ignore(qs)
    transformed = pattern.transform_string(transformed)

    # transformed = (pp.Keyword("except") + ~pp.FollowedBy(pp.Literal(":") | pp.Literal("\n"))).set_parse_action(lambda t: "except:").ignore(qs).transform_string(transformed)
    # transformed = (pp.Keyword("else") + ~pp.FollowedBy(pp.Literal(":") | pp.Literal("\n"))).set_parse_action(lambda t: "else:").ignore(qs).transform_string(transformed)
    #
    # transformed = pp.Keyword("elif").set_parse_action(lambda t: ", " + "elif").ignore(qs).transform_string(transformed)
    # transformed = pp.Keyword("else").set_parse_action(lambda t: ", " + "else").ignore(qs).transform_string(transformed)
    # transformed = pp.Keyword("except").set_parse_action(lambda t: ", " + "except").ignore(qs).transform_string(transformed)


    # print("after 'reader macros'", transformed)
    # sio = io.StringIO(s)
    sio = io.StringIO(transformed)
    transformed = preprocess(sio).getvalue()
    # print("preprocessed", transformed.replace("\x07", "!!!"))

    res = grammar.parseString(transformed, parseAll=True)

    # print("parser:", res)

    res = res[0]

    def replacer(op):
        if not isinstance(op, Node):
            return op
        if isinstance(op, _InfixExpr):
            if isinstance(op.args[0], _InfixExpr):
                op = RedundantParens(args=[op.args[0].args[0]])
            else:
                op = op.args[0]
        # if isinstance(op, UnOp) and op.func == ":" and isinstance(elifliteral := op.args[0], Identifier) and elifliteral.name == "elif":
        #     print("huh")
        #     op = op.args[0]
        # if isinstance(op, ColonBinOp) and op.func == "as":
            # op = RebuiltColon(":", list(reversed(op.args)), _is_as_hack=True)

        if not isinstance(op, Node):
            return op

        op.args = [replacer(arg) for arg in op.args]
        op.func = replacer(op.func)
        return op

    res = replacer(res)

    print("redundant", res)

    return res

if __name__ == "__main__":
    parse("""
if((x=5): print(5) elif x = 4: ohyeah else: "hmm")
""")
    parse("""
# ((((xyz = 12345678))))
# abc = 5
(x = ((5+6)*7))     # Parens(=(x,*(Parens(+(5,6)),7)))
x = ((5+6))*7    # Parens(=(x,Parens(*(Parens(+(5,6)),7))))

foo(x=5, 

(y=5))

if ((x=5):
    print(5)
elif x = 4:
    ohyeah
elif x = 5:
    10
    10
else:
    10
    10
)


""")


    0 and parse("""
class (Foo:
    def (init, x:
        (((xyz = 12345678)))
    )
    def (destroy:
        blah(:
            1
        :
            1
        )
    )
    def (doit, x:
        print("yeah", x)
        if (x:
            return
        )
        x = :y+1 : symbol
        #self.didit(x)
        didit(x)
        #self.x = x
    )
    def (didit, x:
        print("yeah", x)
        def (x:int, y:float, z=x+1:int)
        filter(lambda(c:if(c:x=y:int, elif:x:y=2:int, else:y=3:int)), [0,1,2])
    )
)
""")

    
0 and parse("""
def (foo:int:int:
    #x=1:int
    ("1+
    2")
    1
    (1:
2)
    1
    x=y:int
    x=::int:symbol
    :x
    class (Foo:
        def (init, x:
            pass
        )
        def (destroy:
            pass
        )
        def (doit, x:
            print("yeah", x)
            if (x:
                return
            )
            #self.didit(x)
            didit(x)
            #self.x = x
        )
        def (didit, x:
            print("yeah", x)
            filter(lambda(c:if(c:x=y:int, elif:x:y=2:int, else:0)), [0,1,2])
            def (x:int, y:float, z=x+1:int)
        )
    )
)
""")


"""


class (Foo, x:
    def (doit, x:
        print("yeah", x)
        if (x:
            return
        )
        self.didit(x)
    )
    def (didit, x:
        print("yeah", x)
    )
)

filter(x:
    x == 1
over=[0,1,2])

filter(lambda(c:if(c:x=y:int, elif:x:2, else:0)), [0,1,2])

list (c: 
    print(c)
    c*2
for:
    list (x:
        x+1
    for: 
        list (x in a:
            x+2
        )
    )
if: 
    c > 0
)

list (c: c*2, for: list (x: x+1, for: list (x in a: x+2)), if: c > 0)

list (c in list(x in [0,1,2]: x+1): c*2, if: c > 0)

list (c in list(x in [0,1,2]: x+1): c*2, if: c > 0)

[c*2 for c in [x+1 for x in [0,1,2]] if c > 0]

list (x+1: x in [0,1,2])

list(c*2: c in list(x+1: x in [0,1,2]), if: c > 0)

list(c*2: 
    c in list(x+1: 
        x in [0,1,2]
    )
if: c > 0)

if ( x > 1:
    1
    foo(1, 2)
elf: x > 2:
    2
elf: x > 3:
    4
else:
    return (5)
)

match (x:
    1
case: x:
    2
)

try (:
    bad()
BadError: e:
    pass
IOError: io:
    print(io)
except:
    pass
)

f = lambda (:
    1
)


pymacro (for, context, node:
    if (node.args[1] not iskind InOp:
        raise (SyntaxError("yo"))
    )
        
    for (a in node.args:
        a
    )
)

cppmacro ("if", args, cpp):

    assert (len(args) >= 2)
    for (a in args:
        print(arg)
    )
)

"""


#sys.exit(0)

if __name__ == "__main__" and 0:


    print(listItem.parseString('print("1")', parseAll=True))
    print(listItem.parseString('print(1)', parseAll=True))
    print(listItem.parseString('print([1])', parseAll=True))
    #print(listItem.parseString("[{ 'A':1, 'B':2, 'C': {'a': 1.2, 'b': 3.4}}]", parseAll=True))
    #print(listItem.parseString("print([{ 'A':1, 'B':2, 'C': {'a': 1.2, 'b': 3.4}}])", parseAll=True))
    print(listItem.parseString("foo()()", parseAll=True))
    print(listItem.parseString("foo()()()", parseAll=True))
    print(listItem.parseString("foo(1)('a')()", parseAll=True))
    print(listItem.parseString("foo(1+1)('a')()", parseAll=True))
    print(listItem.parseString("9+3", parseAll=True))
    print(listItem.parseString("9-3-2", parseAll=True))
    print(listItem.parseString("++--1", parseAll=True))
    print(listItem.parseString("-5-2-2", parseAll=True))
    print(listItem.parseString("((-5)-2)-2", parseAll=True))
    print(listItem.parseString("1+foo()", parseAll=True))
    print(listItem.parseString("-foo(foo([]))", parseAll=True))
    print(listItem.parseString("""
        1+1*foo(

        [

        ]
        )
    """, parseAll=True))
    #print(listItem.parseString("foo([1+1,x, (a,1)])", parseAll=True))
    print(listItem.parseString("foo([1+1,x, x*y, (a,)])", parseAll=True).dump())

    print(listItem.parseString("""foo(1, 2,1, 1)""", parseAll=True))

    print(listItem.parseString("""
        foo(1, 2:
            2
            1+2
        3+4:
            1+5
        )
    """, parseAll=True))
    #print(listItem.parseString("foo(:)", parseAll=True))

    print(listItem.parseString("""
        foo(1, 2: 
            (1
        +

        5)

            1+2
            3+4
        )
    """, parseAll=True))

    print(listItem.parseString(
    """if (2: print("yay1") elif: 2:
        1+2
        3+4
    else:
        darn()
    )
    """, parseAll=True))

    print(listItem.parseString(
    """if (2: print("yay1") elif: 2)""", parseAll=True))

    print(listItem.parseString(
    """if (2: 1 elif: 2)""", parseAll=True))

    print(listItem.parseString(
    """if (2: 1 1: 2)""", parseAll=True))

    print(listItem.parseString(
    """if (2: 1 1)""", parseAll=True))

    print(listItem.parseString(
    """if (2: 1 1)""", parseAll=True))

    print(listItem.parseString(
        """if (1:1 :2)""", parseAll=True))

    print(listItem.parseString(
    """
    if (2: foo(1:
        2) 1: 2)""", parseAll=True))

    print(listItem.parseString("""
    if (foo():
        print("yay2")
    elif: x+2:
        1+2
        3+4
    elif:x + 3:
        0
    else: darn())
    """, parseAll=True))

    print(listItem.parseString("""def (foo, x, y, z:
        print("yay2")
        print("yay2")
        x = y : int
        1
    )
    """, parseAll=True))

    print(listItem.parseString("""
        if (foo():
            print("yay2")
            , : x+2
            1+2
            3+4
        , : x + 2
            0
        , else: darn()
        )
    """, parseAll=True))

    print(listItem.parseString("""
        try (e:
            print("yay") 1,,,,
            
        , DarnedError: 
            1+2
            3+4
        , except: darn()
        , finally:
            print(1)
            print(2)
        )
    """, parseAll=True))

    print(listItem.parseString("""
        try (e:
            print("yay")
        , DarnedError: 
            1+2
            3+4
        , except: darn()
        , finally: 0
            print(1)
            if (foo():
                print("yay")
            , elif: x+2
                1+2
                3+4
            , else: darn()
            )
        )
    """, parseAll=True))

    print(listItem.parseString("""
        try (e:
            print("yay")
        , DarnedError: 
            1+2
            3+4
        , except: darn()
        , finally: 0
            print(1)
            if (foo():
                print("yay")
            , elif: x+2
                1+2
                3+4
                try (e:
                    print("yay")
                , DarnedError: 
                    1+2
                    3+4
                , except: darn()
                , finally: 0
                    print(1)
                    if (foo():
                        print("yay")
                    , elif: x+2
                        1+2
                        3+4
                    , else: darn()
                        try (e:
                            print("yay")
                        , DarnedError: 
                            1+2
                            3+4
                        , except: darn()
                        , finally: 0
                            print(1)
                            if (foo():
                                print("yay")
                            , elif: x+2
                                1+2
                                3+4
                                try (e:
                                    print("yay")
                                , DarnedError: 
                                    1+2
                                    3+4
                                , except: darn()
                                , finally: 0
                                    print(1)
                                    if (foo():
                                        print("yay")
                                    , elif: x+2
                                        1+2
                                        3+4
                                    , else: darn()
                                    )
                                )
                            , else: darn()
                            )
                        )
                    )
                )
            , else: darn()
            )
        )
    """, parseAll=True))

    print(listItem.parseString("""
        if (:x+5, :y+4, 5) + 5
    """, parseAll=True))

    0 and expr.runTests(
        """\
        print("Hello, World!")
        (lookup_function("fprintf"))(stderr, "Hello, World!")
        """,
        fullDump=False,
    )


# parsePythonValue.py
#
# Copyright, 2006, by Paul McGuire
#



if __name__ == "__main__" and 0:

    tests = """['a', 100, ('A', [101, 102]), 3.14, [ +2.718, 'xyzzy', -1.414] ]
               [{0: [2], 1: []}, {0: [], 1: [], 2: []}, {0: [1, 2]}]
               { 'A':1, 'B':2, 'C': {'a': 1.2, 'b': 3.4} }
               3.14159
               42
               6.02E23
               6.02e+023
               1.0e-7
               'a quoted string'"""

    #listItem.runTests(tests)
    print(listItem.parseString("""
    [42,
    43]
""", parseAll=True))
