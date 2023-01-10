#
# Based on the pyparsing examples: parsePythonValue.py, left_recursion.py, simpleBool.py
#
# 
#
import pyparsing as pp

import sys
sys.setrecursionlimit(2**13)
# pp.ParserElement.enable_left_recursion()
pp.ParserElement.enable_packrat(2**20)

import io

from preprocessor import preprocess


class ParserError(Exception):
    pass


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


class RebuiltBinOp(BinOp):
    def __init__(self, func, args):
        self.func = func
        self.args = args


class _LeftAssociativeBinOp(BinOp):
    pass


def _make_left_associative_bin_op_init_method(astclass = _LeftAssociativeBinOp):
    def __init__(self, tokens):
        t = tokens[0]
        last_arg = t[-1]
        last_op = t[-2]
        self.func = last_op
        if len(t) > 3:
            beg = t[0:-2]
            self.args = [astclass(pp.ParseResults([beg])), last_arg]
        else:
            self.args = [t[0], last_arg]
    return __init__


_LeftAssociativeBinOp.__init__ = _make_left_associative_bin_op_init_method()


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


class AttributeAccess(_LeftAssociativeBinOp):

    def __repr__(self):
        return "{}.{}".format(self.lhs, self.rhs)


AttributeAccess.__init__ = _make_left_associative_bin_op_init_method(AttributeAccess)


# not created by parser
class ArrowOp(BinOp):  # doesn't get special auto deref logic of '.' (use at own risk)
    def __init__(self, args):
        self.func = "->"
        self.args = args


class ScopeResolution(BinOp):
    def __init__(self, args):
        self.func = "::"
        self.args = args


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

    def __init__(self, t):
        tokens = t.as_list()
        if len(tokens) == 2:
            self.func = tokens[0]
            args = tokens[1]
        else:
            assert len(tokens) > 2
            self.func = Call(pp.ParseResults(tokens[:-1]))
            args = tokens[-1]

        lpar = args.pop(0)
        _ = args.pop() # rpar
        self._is_array = lpar == "["
        self.args = args

        # print("callargs", self.args)
        # print("done")


class ArrayAccess(Node):
    def __repr__(self):
        return "{}[{}]".format(self.func, ",".join(map(str, self.args)))

    def __init__(self, func, args):
        self.func = func
        self.args = args

# class ArrayAccess(Node):
#     def __repr__(self):
#         return "{}[{}]".format(self.func, ",".join(map(str, self.args)))
#
#     def __init__(self, tokens):
#         # self.func = tokens[0]
#         # self.args = tokens.as_list()[1:]
#         tokens = tokens.as_list()
#         if len(tokens) == 2:
#             self.func = tokens[0]
#             self.args = tokens[1]
#         else:
#             assert len(tokens) > 2
#             self.func = ArrayAccess(pp.ParseResults(tokens[:-1]))
#             self.args = tokens[-1]


class TemplateSpecialization(Node):
    def __repr__(self):
        return "{}<{}>".format(self.func, ",".join(map(str, self.args)))

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
        self.func = None #int(token[0])
        self.args = []
        self.integer = int(token[0])

    def __repr__(self):
        return str(self.integer)


class RebuiltInteger(IntegerLiteral):

    def __init__(self, integer):
        self.integer = integer
        self.func = None
        self.args = []



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


class BracedLiteral(_ListLike):

    def __init__(self, tokens):
        super().__init__(tokens)
        self.func = None  #


class Block(_ListLike):

    def __init__(self, tokens):
        super().__init__(tokens)
        self.func = "Block"


class Module(Block):
    def __init__(self, tokens):
        super().__init__(tokens)
        self.func = "Module"


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
    dict_literal = pp.Forward()
    braced_literal = pp.Forward()
    function_call = pp.Forward()
    template_specialization = pp.Forward()
    infix_expr = pp.Forward()
    ident = pp.Word(pp.alphas + "_", pp.alphanums + "_").set_parse_action(Identifier)

    quoted_str = pp.QuotedString("'", multiline=True).set_parse_action(StringLiteral)
    dblquoted_str = pp.QuotedString('"', multiline=True).set_parse_action(StringLiteral)
    cdblquoted_str = pp.Suppress(pp.Keyword("c")) + pp.QuotedString('"', multiline=True).set_parse_action(CStringLiteral)

    atom = (
        real
        | integer
        | cdblquoted_str
        | quoted_str
        | dblquoted_str
        | list_literal
        | tuple_literal
        | dict_literal
        | braced_literal
        | ident
    )

    expop = pp.Literal("^")
    signop = pp.oneOf("+ -")
    multop = pp.oneOf("* / %")
    plusop = pp.oneOf("+ -")
    colon = pp.Literal(":")
    dot = pp.Literal(".")

    _compar_atoms = list(map(pp.Literal, ["<", "<=",  ">",  ">=", "!=", "=="]))
    _compar_atoms.extend(map(pp.Keyword, ["in", "not in", "is", "is not"]))
    comparisons = _compar_atoms.pop()
    for c in _compar_atoms:
        comparisons |= c

    def andanderror(*t):
        raise ParserError("don't use '&&'. use 'and' instead.", *t)

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

    dict_entry = pp.Group(infix_expr + bel + infix_expr)
    dict_literal <<= (lbrace + pp.delimited_list(dict_entry, min=1, allow_trailing_delim=True) + rbrace)

    braced_literal <<= (lbrace + pp.Optional(pp.delimited_list(dict_entry)) + rbrace).set_parse_action(BracedLiteral)

    block_line_end = pp.Suppress(";")
    block = bel + pp.OneOrMore(infix_expr + pp.OneOrMore(block_line_end)).set_parse_action(Block)

    ack = pp.Suppress("\x06")
    template_specialization <<= ((atom | (lparen + infix_expr + rparen)) + pp.Suppress("<") + pp.delimitedList(infix_expr) + pp.Suppress(">") + pp.Optional(ack)).set_parse_action(TemplateSpecialization)

    non_block_args = pp.Optional(pp.delimited_list(pp.Optional(infix_expr)))

    # don't pp.Suppress these to allow post-parse array vs call detection
    lparen = pp.Literal("(")
    rparen = pp.Literal(")")
    lbrack = pp.Literal("[")
    rbrack = pp.Literal("]")

    array_access_args = lbrack + infix_expr + pp.Optional(bel + infix_expr) + pp.Optional(bel + infix_expr) + rbrack

    call_args = lparen + non_block_args + pp.ZeroOrMore(block + non_block_args) + rparen

    function_call <<= ((template_specialization | atom | (pp.Suppress("(") + infix_expr + pp.Suppress(")"))) + pp.OneOrMore(pp.Group(call_args|array_access_args))).set_parse_action(Call)

    infix_expr <<= pp.infix_notation(
        function_call | template_specialization | atom,
        [
            (pp.Literal("::"), 2, pp.opAssoc.LEFT, AttributeAccess),
            (pp.Literal("&&"), 2, pp.opAssoc.LEFT, andanderror),  # avoid interpreting a&&b as a&(&b)
            (dot|pp.Literal("->"), 2, pp.opAssoc.LEFT, AttributeAccess),
            (pp.Keyword("not") | pp.Literal("*") | pp.Literal("&"), 1, pp.opAssoc.RIGHT, UnOp),
            (expop, 2, pp.opAssoc.RIGHT, BinOp),
            (signop, 1, pp.opAssoc.RIGHT, UnOp),
            (multop, 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (plusop, 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            ((pp.Literal("<<")|pp.Literal(">>")), 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (pp.Literal("<=>"), 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (comparisons, 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            # TODO: maybe move 'not' here like python? (with parenthesese in codegen)
            (pp.Literal("&"), 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (pp.Literal("^"), 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (pp.Literal("|"), 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (pp.Keyword("and"), 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (pp.Keyword("or"), 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (colon, 2, pp.opAssoc.RIGHT, ColonBinOp),
            ("=", 2, pp.opAssoc.RIGHT, Assign),
            (pp.Keyword("return")|pp.Keyword("yield"), 1, pp.opAssoc.RIGHT, UnOp),
        ],
    ).set_parse_action(_InfixExpr)

    module = pp.OneOrMore(infix_expr + block_line_end).set_parse_action(Module)

    return module

grammar = _create()


def parse(s):
    print(s)
    # pp.ParserElement.set_default_whitespace_chars(" \t\n")

    filter_comments = pp.Regex(r"#.*")
    filter_comments = filter_comments.suppress()
    qs = pp.QuotedString('"') | pp.QuotedString("'")
    filter_comments = filter_comments.ignore(qs)

    transformed = s

    transformed = filter_comments.transform_string(transformed)

    # pp.ParserElement.set_default_whitespace_chars(" \t")

    patterns = [(pp.Keyword(k) + ~pp.FollowedBy(pp.Literal(":") | pp.Literal("\n"))) for k in ["elif", "except"]]
    pattern = None
    for p in patterns:
        p = p.set_parse_action(lambda t: t[0] + ":")
        if pattern is None:
            pattern = p
        pattern |= p

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

    sio = io.StringIO(transformed)
    transformed = preprocess(sio).getvalue()
    print(transformed.replace("\x07", "!!!").replace("\x06", "&&&"))

    res = grammar.parseString(transformed, parseAll=True)

    res = res[0]

    def replacer(op):
        if not isinstance(op, Node):
            return op

        if isinstance(op, _InfixExpr):
            if isinstance(op.args[0], _InfixExpr):
                op = RedundantParens(args=[op.args[0].args[0]])
            else:
                op = op.args[0]

        if isinstance(op, AttributeAccess):
            if op.func == "->":
                op = ArrowOp(op.args)
            elif op.func == "::":
                op = ScopeResolution(op.args)
        elif isinstance(op, Call):
            if op._is_array:
                op = ArrayAccess(op.func, op.args)

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
