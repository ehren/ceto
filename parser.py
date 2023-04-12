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
        self.func = tokens[0][0]  # TODO should be an Identifier
        self.args = [tokens[0][1]]


class LeftAssociativeUnOp(Node):
    def __init__(self, tokens):
        self.func = tokens[0][1]  # TODO should be an Identifier
        self.args = [tokens[0][0]]



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


class TypeOp(BinOp):
    def __init__(self, tokens):
        super().__init__(tokens)
        if self.func == "as":
            self.args = list(reversed(self.args))
            self.func = ":"


class RebuiltColon(TypeOp):
    def __init__(self, func, args, _is_as_hack=False):
        self.func = func
        self.args = args
        self._is_as_hack = _is_as_hack


class SyntaxTypeOp(TypeOp):
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

    def __init__(self, t):
        # manual left associative parse tree creation:
        self.func = "::"
        t = t.as_list()
        if len(t) > 2:
            last = t[-1]
            beg = t[0:-1]
            self.args = [ScopeResolution(pp.ParseResults(beg))] + [last]
        else:
            self.args = t


class RebuiltScopeResolution(ScopeResolution):

    def __init__(self, func, args):
        self.func = func
        self.args = args

class RebuiltAttributeAccess(AttributeAccess):

    def __init__(self, func, args):
        self.func = func
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

    def __init__(self, func, args):
        self.func = func
        self.args = args



    def __init2__(self, t):
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
        self._is_braced_call = lpar == "{"
        self.args = args

        # print("callargs", self.args)
        # print("done")


def call_parse_action(s, l, t):
    tokens = t.as_list()

    if len(tokens) == 2:
        func = tokens[0]
        args = tokens[1]
    else:
        assert len(tokens) > 2
        func = call_parse_action(s, l, pp.ParseResults(tokens[:-1]))  # left-associative
        args = tokens[-1]

    # res = Call(func, args)

    scope_resolve_part = args.pop()

    leading_punctuation = args.pop(0)
    if leading_punctuation == "(":
        end_punctuation = args.pop()
        assert end_punctuation == ")"
        call = Call(func, args)
    elif leading_punctuation == "[":
        end_punctuation = args.pop()
        assert end_punctuation == "]"
        call = ArrayAccess(func, args)
    elif leading_punctuation == "{":
        end_punctuation = args.pop()
        assert end_punctuation == "}"
        call = BracedCall(func, args)
    else:
        print("fatal parse error. unexpected scope resolved call.", file=sys.stderr)
        sys.exit(-1)

    if scope_resolve_part:
        scope_op, scope_op_rhs = scope_resolve_part

        if scope_op == ".":
            return RebuiltAttributeAccess(func=".", args=[call, scope_op_rhs])
        elif scope_op == "->":
            return ArrowOp(args=[call, scope_op_rhs])
        elif scope_op == "::":
            return RebuiltScopeResolution(func="::", args=[call, scope_op_rhs])

    return call


class ArrayAccess(Node):
    def __repr__(self):
        return "{}[{}]".format(self.func, ",".join(map(str, self.args)))

    def __init__(self, func, args):
        self.func = func
        self.args = args


class BracedCall(Node):
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


class Template(Node):
    # template-id in proper standardese
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
        self.func = "Braced"


class Block(_ListLike):

    def __init__(self, tokens):
        super().__init__(tokens)
        self.func = "Block"


class Module(Block):
    def __init__(self, tokens):
        super().__init__(tokens)
        self.func = "Module"
        self.has_main_function = False


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
    template = pp.Forward()
    scope_resolution = pp.Forward()
    scope_resolved_call = pp.Forward()
    infix_expr = pp.Forward()
    ident = pp.Word(pp.alphas + "_", pp.alphanums + "_").set_parse_action(Identifier)

    quoted_str = pp.QuotedString("'", multiline=True, esc_char="\\").set_parse_action(StringLiteral)
    dblquoted_str = pp.QuotedString('"', multiline=True, esc_char="\\").set_parse_action(StringLiteral)
    cdblquoted_str = pp.Suppress(pp.Keyword("c")) + pp.QuotedString('"', multiline=True).set_parse_action(CStringLiteral)

    atom = (
        template
        | real
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

    braced_literal <<= (lbrace + pp.Optional(pp.delimited_list(infix_expr)) + rbrace).set_parse_action(BracedLiteral)

    block_line_end = pp.Suppress(";")
    block = pp.Suppress(":") + bel + pp.OneOrMore(infix_expr + pp.OneOrMore(block_line_end)).set_parse_action(Block)

    ack = pp.Suppress("\x06")
    template <<= ((ident | (lparen + infix_expr + rparen)) + pp.Suppress("<") + pp.delimitedList(infix_expr) + pp.Suppress(">") + pp.Optional(ack)).set_parse_action(Template)

    non_block_args = pp.Optional(pp.delimited_list(pp.Optional(infix_expr)))

    # don't pp.Suppress these to allow post-parse array vs call detection
    unsupressed_lparen = pp.Literal("(")
    unsupressed_rparen = pp.Literal(")")
    unsupressed_lbrack = pp.Literal("[")
    unsupressed_rbrack = pp.Literal("]")
    unsupressed_lbrace = pp.Literal("{")
    unsupressed_rbrace = pp.Literal("}")

    array_access_args = unsupressed_lbrack + infix_expr + pp.Optional(bel + infix_expr) + pp.Optional(bel + infix_expr) + unsupressed_rbrack

    braced_args = unsupressed_lbrace + pp.Optional(pp.delimited_list(infix_expr)) + unsupressed_rbrace

    call_args = unsupressed_lparen + non_block_args + pp.ZeroOrMore(block + non_block_args) + unsupressed_rparen

    dot = pp.Literal(".")
    arrow_op = pp.Literal("->")

    scope_resolution <<= pp.infix_notation(atom|(pp.Suppress("(") + infix_expr + pp.Suppress(")")), [
            (pp.Literal("::"), 2, pp.opAssoc.LEFT, AttributeAccess),
            (dot|arrow_op, 2, pp.opAssoc.LEFT, AttributeAccess),
    ])

    call_func = (scope_resolution) #| (pp.Suppress("(") + infix_expr + pp.Suppress(")")))
    # call_func = (scope_resolution | scope_resolved_call | (pp.Suppress("(") + infix_expr + pp.Suppress(")")))

    # function_call <<= (call_func + pp.OneOrMore(pp.Group(call_args|array_access_args|braced_args))).set_parse_action(Call)

    function_call <<= (call_func + pp.OneOrMore(pp.Group((call_args|array_access_args|braced_args) + pp.Group(pp.Optional((pp.Literal("::")|pp.Literal(".")|pp.Literal("->")) + scope_resolution))))).set_parse_action(call_parse_action)

    # scope_resolved_call <<= pp.infix_notation(function_call, [
    #     (pp.Literal("::"), 2, pp.opAssoc.LEFT, AttributeAccess),
    #     (dot|arrow_op, 2, pp.opAssoc.LEFT, AttributeAccess),
    # ])

    signop = pp.oneOf("+ -")
    multop = pp.oneOf("* / %")
    plusop = pp.oneOf("+ -")
    colon = pp.Literal(":")
    not_op = pp.Keyword("not")
    star_op = pp.Literal("*")
    amp_op = pp.Literal("&")
    ellipsis_op = pp.Literal("...")

    _compar_atoms = list(map(pp.Literal, ["<", "<=",  ">",  ">=", "!=", "=="]))
    _compar_atoms.extend(map(pp.Keyword, ["in", "not in", "is", "is not"]))
    comparisons = _compar_atoms.pop()
    for c in _compar_atoms:
        comparisons |= c

    def andanderror(*t):
        raise ParserError("don't use '&&'. use 'and' instead.", *t)

    infix_expr <<= pp.infix_notation(
        function_call|scope_resolution,
        [
            (pp.Literal("&&"), 2, pp.opAssoc.LEFT, andanderror),  # avoid interpreting a&&b as a&(&b)
            # (pp.Literal("::"), 2, pp.opAssoc.LEFT, AttributeAccess),
            # (dot|arrow_op, 2, pp.opAssoc.LEFT, AttributeAccess),
            (not_op | star_op | amp_op, 1, pp.opAssoc.RIGHT, UnOp),
            # (expop, 2, pp.opAssoc.RIGHT, BinOp),
            (signop, 1, pp.opAssoc.RIGHT, UnOp),
            (multop, 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (plusop, 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            ((pp.Literal("<<")|pp.Literal(">>")), 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (pp.Literal("<=>"), 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (comparisons, 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            # TODO: maybe move 'not' here like python? (with parenthesese in codegen)
            (amp_op, 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (pp.Literal("^"), 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (pp.Literal("|"), 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (pp.Keyword("and"), 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (pp.Keyword("or"), 2, pp.opAssoc.LEFT, _LeftAssociativeBinOp),
            (colon, 2, pp.opAssoc.RIGHT, TypeOp),
            ("=", 2, pp.opAssoc.RIGHT, Assign),
            (pp.Keyword("return")|pp.Keyword("yield"), 1, pp.opAssoc.RIGHT, UnOp),
            (ellipsis_op, 1, pp.opAssoc.LEFT, LeftAssociativeUnOp),
        ],
    ).set_parse_action(_InfixExpr)

    module = pp.OneOrMore(infix_expr + block_line_end).set_parse_action(Module)

    return module

grammar = _create()


def do_parse(source: str):
    # TODO consider making "elif" "else" and "except" genuine UnOps (sometimes identifiers in the 'else' case) rather than relying on ':' ',' insertion (to make one liners more ergonomic and remove need for extra semicolon in 'elif: x:'

    patterns = [(pp.Keyword(k) + ~pp.FollowedBy(pp.Literal(":") | pp.Literal("\n"))) for k in ["elif", "except"]]
    pattern = None
    for p in patterns:
        p = p.set_parse_action(lambda t: t[0] + ":")
        if pattern is None:
            pattern = p
        pattern |= p

    qs = pp.QuotedString('"') | pp.QuotedString("'")
    pattern = pattern.ignore(qs)
    source = pattern.transform_string(source)

    patterns = [pp.Keyword(k) for k in ["elif", "else", "except"]]
    pattern = None
    for p in patterns:
        p = p.set_parse_action(lambda t: "," + t[0])
        if pattern is None:
            pattern = p
        pattern |= p

    pattern = pattern.ignore(qs)
    source = pattern.transform_string(source)

    print(source.replace("\x07", "!!!").replace("\x06", "&&&"))

    res = grammar.parseString(source, parseAll=True)
    return res[0]


def parse(source: str):
    from textwrap import dedent

    sio = io.StringIO(source)
    preprocessed, _, _ = preprocess(sio, reparse=False)
    preprocessed = preprocessed.getvalue()

    try:
        res = do_parse(preprocessed)
    except pp.ParseException as orig:
        sio.seek(0)
        reparse, replacements, subblocks = preprocess(sio, reparse=True)
        reparse = reparse.getvalue()

        try:
            do_parse(reparse)
        except pp.ParseException:

            for (lineno, colno), block in subblocks:
                # dedented = dedent(block)

                try:
                    # do_parse(dedented)
                    do_parse(block)
                except pp.ParseException as blockerror:
                    print("blockerr")
                    blockerror._ceto_col = blockerror.col# + colno
                    blockerror._ceto_lineno =   blockerror.lineno -  1
                    raise blockerror

        for dummy, real in replacements.items():
            # dedented = dedent(real)
            try:
                # do_parse(dedented)
                do_parse(real)
            except pp.ParseException as lineerror:
                print("lineerr")
                dummy = dummy[len('ceto_priv_dummy'):-1]
                line, col = dummy.split("c")
                lineerror._ceto_col = int(col) + lineerror.col - 1
                # lineerror._ceto_col = lineerror.col
                lineerror._ceto_lineno = int(line)# + lineerror.lineno
                raise lineerror

        raise orig


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
                op = RebuiltScopeResolution(op.func, op.args)
        elif isinstance(op, Call):

            pass

            # this can be fixed by refactoring parse actions from classes to plain functions (that construct the appropriate class inline)
            # if op._is_array:
            #     op = ArrayAccess(op.func, op.args)
            # elif op._is_braced_call:
            #     op = BracedCall(op.func, op.args)

            # we've also got an annoying precedence issues left for the case:
            # Blah()::foo.method()
            # parsed as ScopeResolution(Call(Blah, []), Call(AttributeAccess(foo,method), []))
            # should be
            # Call(AttributeAccess(ScopeResolution(Call(Blah, []), foo), method), [])

        if not isinstance(op, Node):
            return op

        op.args = [replacer(arg) for arg in op.args]
        op.func = replacer(op.func)
        return op

    res = replacer(res)

    print("final parse:", res)

    return res