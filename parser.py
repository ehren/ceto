#
# Based on the pyparsing examples: parsePythonValue.py, left_recursion.py, simpleBool.py
#
# 
#
import pyparsing as pp

import io

from preprocessor import preprocess


class Node:

    def __repr__(self):
        return "{}({})({!r})".format(self.__class__.__name__,
                                     self.func, self.args)


class UnOp(Node):
    def __init__(self, tokens):
        self.func = tokens[0][0]
        self.args = [tokens[0][1]]


class BinOp(Node):
    def __init__(self, tokens):
        self.func = tokens[0][1]
        self.args = tokens[0][::2]

    def __repr__(self):
        return "{}({})".format(self.func, ",".join(map(str,self.args)))


class ColonBinOp(BinOp):
    pass


class Assign(BinOp):
    pass


# this introduces an "implicit" outer Parens around every infix expression
# but it allows us to preserve truly redundant parentheses (to ascribe special meaning)
# We remove the implicit outer Parens after parsing
class Parens(Node):
    def __init__(self, t):
        self.func = "Parens"
        self.args = [t.as_list()[0]]

    def __repr__(self):
        return "{}({})".format(self.func, ",".join(map(str, self.args)))


class RedundantParens(Parens):
    def __init__(self, args):
        self.func = "RedundantParens"
        self.args = args



class Call(Node):
    def __repr__(self):
        return "{}({})".format(self.func, ",".join(map(str,self.args)))

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


class IntegerLiteral(Node):
    def __init__(self, token):
        self.func = int(token[0])
        self.args = []

    def __repr__(self):
        return str(self.func)


class ListLike(Node):
    def __repr__(self):
        return "{}({!r})".format(self.func, self.args)

    def __init__(self, tokens):
        self.func = "ListLikeOperator"
        self.args = tokens.as_list()


class Block(Node):
    def __repr__(self):
        return "{}({})".format(self.func, ",".join(map(str, self.args)))

    def __init__(self, tokens):
        self.func = "Block"

        self.args = [t[0] for t in tokens.as_list()]


class Module(ListLike):
    def __init__(self, tokens):
        super().__init__(tokens)
        self.func = "Module"


def create():

    pp.ParserElement.enableLeftRecursion()

    cvtBool = lambda t: t[0] == "True"
    cvtInt = lambda toks: int(toks[0])
    cvtReal = lambda toks: float(toks[0])
    cvtTuple = lambda toks: tuple(toks.asList())
    cvtDict = lambda toks: dict(toks.asList())
    cvtList = lambda toks: [toks.asList()]

    # define punctuation as suppressed literals
    lparen, rparen, lbrack, rbrack, lbrace, rbrace, comma = map(
        pp.Suppress, "()[]{},"
    )

    integer = pp.Regex(r"[+-]?\d+").setName("integer").setParseAction(IntegerLiteral)
    real = pp.Regex(r"[+-]?\d+\.\d*([Ee][+-]?\d+)?").setName("real").setParseAction(cvtReal)
    tupleStr = pp.Forward()
    listStr = pp.Forward()
    dictStr = pp.Forward()
    function_call = pp.Forward()
    infix_expr = pp.Forward()
    ident = pp.Word(pp.alphas + "_", pp.alphanums + "_").setParseAction(Identifier)

    #unistr = pp.unicodeString(multiline=True).setParseAction(lambda t: t[0][2:-1])
    quoted_str = pp.QuotedString("'", multiline=True).setParseAction(lambda t: "string:"+t[0])    #.setParseAction(lambda t: t[0][1:-1])
    dblquoted_str = pp.QuotedString('"', multiline=True).setParseAction(lambda t: "string"+t[0])   #  .setParseAction(lambda t: t[0][1:-1])

    boolLiteral = pp.oneOf("True False", asKeyword=True).setParseAction(cvtBool)
    noneLiteral = pp.Keyword("None").setParseAction(pp.replaceWith(None))

    expr = (
        function_call
        | real
        | integer
        | quoted_str
        | dblquoted_str
        | boolLiteral
        | noneLiteral
        | pp.Group(listStr)
        | tupleStr
        | dictStr
        | ident
    )

    expop = pp.Literal("^")
    signop = pp.oneOf("+ -")
    multop = pp.oneOf("* /")
    plusop = pp.oneOf("+ -")
    factop = pp.Literal("!")
    colon = pp.Literal(":")

    infix_expr <<= pp.infix_notation(
        expr,
        [
            ("!", 1, pp.opAssoc.LEFT, UnOp),
            ("^", 2, pp.opAssoc.RIGHT, BinOp),
            (signop, 1, pp.opAssoc.RIGHT, UnOp),
            (multop, 2, pp.opAssoc.LEFT, BinOp),
            (plusop, 2, pp.opAssoc.LEFT, BinOp),
            ("=", 2, pp.opAssoc.RIGHT, Assign),
            (colon, 1, pp.opAssoc.RIGHT, UnOp),  # unary : shold bind less tight than binary
            (colon, 2, pp.opAssoc.RIGHT, ColonBinOp),
        ],
    ).setParseAction(Parens)

    tupleStr <<= (
        lparen + pp.delimitedList(infix_expr) + pp.Optional(comma) + rparen
    )

    listStr <<= (
        lbrack + pp.Optional(pp.delimitedList(infix_expr) + pp.Optional(comma)) + rbrack
    )

    dictEntry = pp.Group(infix_expr + pp.Suppress("@@@") + infix_expr)
    dictStr <<= (
        lbrace + pp.Optional(pp.delimitedList(dictEntry) + pp.Optional(comma)) + rbrace
    )

    gs = '\x1D'
    rs = '\x1E'
    block_start = pp.Suppress(gs)
    block_line_end = pp.Suppress(rs)

    block = block_start + pp.OneOrMore(pp.Group(infix_expr + block_line_end)).setParseAction(Block)

    function_call <<= ((expr | (lparen + infix_expr + rparen)) + lparen + pp.Optional(pp.delimitedList(infix_expr)) + pp.ZeroOrMore(block + pp.Optional(pp.delimitedList(infix_expr))) + rparen).setParseAction(Call)

    module = pp.OneOrMore(infix_expr + block_line_end).setParseAction(Module)
    return module

grammar = create()


def parse(s):
    print(s)
    sio = io.StringIO(s)
    transformed = preprocess(sio).getvalue()
    print("preprocessed", transformed.replace("\x1E", "!!!").replace("\x1D", "+++"))

    filter_comments = pp.Regex(r"#.*")
    filter_comments = filter_comments.suppress()
    qs = pp.QuotedString('"') | pp.QuotedString("'")
    filter_comments = filter_comments.ignore(qs)
    transformed = filter_comments.transformString(transformed)

    res = grammar.parseString(transformed, parseAll=True)

    print("parser:", res)

    res = res[0]

    def replacer(op):
        if not isinstance(op, Node):
            return op
        if isinstance(op, Parens):
            if isinstance(op.args[0], Parens):
                op = RedundantParens(args=[op.args[0].args[0]])
            else:
                op = op.args[0]
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
# ((((xyz = 12345678))))
# abc = 5
(x = ((5+6)*7))     # Parens(=(x,*(Parens(+(5,6)),7)))
x = ((5+6))*7    # Parens(=(x,Parens(*(Parens(+(5,6)),7))))

foo(x=5, (y=5))

if ((x=5):
    print(5)
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
