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


def parse_right_unop(s, l, t):
    source = s, l
    func = t[0][0]  # TODO should be an Identifier
    args = [t[0][1]]
    u = UnOp(func, args, source)
    return u


def parse_left_unop(s, l, t):
    func = t[0][1]  # TODO should be an Identifier
    args = [t[0][0]]
    source = s, l
    u = LeftAssociativeUnOp(func, args, source)
    return u


def parse_right_associative_bin_op(s, l, t):
    args = t[0][::2]
    func = t[0][1]
    source = s, l

    if func == ":":
        b = TypeOp(func, args, source)
    elif func == "=":
        b = Assign(func, args, source)
    else:
        b = BinOp(func, args, source)
    return b


def parse_left_associative_bin_op(s, l, t):
    t = t[0]
    last_arg = t[-1]
    last_op = t[-2]
    func = last_op
    if len(t) > 3:
        beg = t[0:-2]
        args = [parse_left_associative_bin_op(s, l, pp.ParseResults([beg])), last_arg]
    else:
        args = [t[0], last_arg]
    source = s, l

    if func == ".":
        b = AttributeAccess(func, args, source)
    elif func == "->":
        b = ArrowOp(func, args, source)
    elif func == "::":
        b = ScopeResolution(func, args, source)
    else:
        b = BinOp(func, args, source)
    return b


# this introduces an implicit wrapper node around every infix expression
# but it allows us to preserve truly redundant parentheses by checking for
# double wrapped nodes. (e.g. assignment expression instead of named parameter
# in call requires one set extra parens)
class _InfixExpr(Node):
    def __init__(self, s, l, t):
        self.func = "_InfixExpr"
        self.args = [t.as_list()[0]]
        source = s, l
        super().__init__(self.func, self.args, source)

    def __repr__(self):
        return "{}({})".format(self.func, ",".join(map(str, self.args)))


# Note: This is not created by the parser (later used to signify non-named parameters)
class RedundantParens(Node):
    def __init__(self, args):
        self.func = "RedundantParens"
        self.args = args
        super().__init__(self.func,self.args,None)


class Call(Node):
    def __repr__(self):
        return "{}({})".format(self.func, ",".join(map(str, self.args)))


class ArrayAccess(Node):
    def __repr__(self):
        return "{}[{}]".format(self.func, ",".join(map(str, self.args)))


class BracedCall(Node):
    def __repr__(self):
        return "{}[{}]".format(self.func, ",".join(map(str, self.args)))


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

    source = s, l

    scope_resolve_part = args.pop()

    leading_punctuation = args.pop(0)
    if leading_punctuation == "(":
        end_punctuation = args.pop()
        assert end_punctuation == ")"
        call = Call(func, args, source)
    elif leading_punctuation == "[":
        end_punctuation = args.pop()
        assert end_punctuation == "]"
        call = ArrayAccess(func, args, source)
    elif leading_punctuation == "{":
        end_punctuation = args.pop()
        assert end_punctuation == "}"
        call = BracedCall(func, args, source)
    else:
        print("fatal parse error. unexpected scope resolved call.", file=sys.stderr)
        sys.exit(-1)

    if scope_resolve_part:
        scope_op, scope_op_rhs = scope_resolve_part

        if scope_op == ".":
            return AttributeAccess(func=scope_op, args=[call, scope_op_rhs], source=source)
        elif scope_op == "->":
            return ArrowOp(func=scope_op, args=[call, scope_op_rhs], source=source)
        elif scope_op == "::":
            return ScopeResolution(func=scope_op, args=[call, scope_op_rhs], source=source)

    return call


class Template(Node):
    # template-id in proper standardese
    def __repr__(self):
        return "{}<{}>".format(self.func, ",".join(map(str, self.args)))

    def __init__(self, s, l, tokens):
        func = tokens[0]
        args = tokens.as_list()[1:]
        source = s, l
        super().__init__(func, args, source)


class Identifier(Node):
    def __init__(self, name, source):
        super().__init__(None, [], source)
        self.name = name

    def __repr__(self):
        return self.name


def parse_identifier(s, l, t):
    name = str(t[0])
    source = s, l
    return Identifier(name, source)


class StringLiteral(Node):
    def __init__(self, s, l, token):
        func = str(token[0])
        args = []
        source = s,l
        super().__init__(func, args, source)


    def __repr__(self):
        # escaped = self.func.translate(str.maketrans({"\n": r"\n" }))
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


def parse_integer_literal(s, l, t):
    integer = int(t[0])
    source = s, l
    return IntegerLiteral(integer, source)


class ListLiteral(Node):
    pass


def parse_list_literal(s, l, t):
    func = None
    args = t.as_list()
    source = s, l
    return ListLiteral(func, args, source)


class TupleLiteral(Node):
    pass


def parse_tuple_literal(s, l, t):
    func = None
    args = t.as_list()
    source = s, l
    return TupleLiteral(func, args, source)


class BracedLiteral(Node):
    pass


def parse_braced_literal(s, l, t):
    func = None
    args = t.as_list()
    source = s, l
    return BracedLiteral(func, args, source)


class Block(Node):

    def __init__(self, args):
        super().__init__(None, args, None)


class Module(Block):
    def __init__(self, args):
        self.has_main_function = False
        super().__init__(args)


def parse_block(s, l, t):
    args = t.as_list()
    return Block(args)


def parse_module(s, l, t):
    args = t.as_list()
    return Module(args)


def _create():

    cvtReal = lambda toks: float(toks[0])

    # define punctuation as suppressed literals
    lparen, rparen, lbrack, rbrack, lbrace, rbrace, comma = map(
        pp.Suppress, "()[]{},"
    )

    integer = pp.Regex(r"[+-]?\d+").setName("integer").set_parse_action(parse_integer_literal)
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
    ident = pp.Word(pp.alphas + "_", pp.alphanums + "_").set_parse_action(parse_identifier)

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
    ).set_parse_action(parse_tuple_literal)

    list_literal <<= (
        lbrack + pp.Optional(pp.delimitedList(infix_expr) + pp.Optional(comma)) + rbrack
    ).set_parse_action(parse_list_literal)

    bel = pp.Suppress('\x07')

    dict_entry = pp.Group(infix_expr + bel + infix_expr)
    dict_literal <<= (lbrace + pp.delimited_list(dict_entry, min=1, allow_trailing_delim=True) + rbrace)

    braced_literal <<= (lbrace + pp.Optional(pp.delimited_list(infix_expr)) + rbrace).set_parse_action(parse_braced_literal)

    block_line_end = pp.Suppress(";")
    block = pp.Suppress(":") + bel + pp.OneOrMore(infix_expr + pp.OneOrMore(block_line_end)).set_parse_action(parse_block)

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
            (pp.Literal("::"), 2, pp.opAssoc.LEFT, parse_left_associative_bin_op),
            (dot|arrow_op, 2, pp.opAssoc.LEFT, parse_left_associative_bin_op),
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
            (not_op | star_op | amp_op, 1, pp.opAssoc.RIGHT, parse_right_unop),
            # (expop, 2, pp.opAssoc.RIGHT, BinOp),
            (signop, 1, pp.opAssoc.RIGHT, parse_right_unop),
            (multop, 2, pp.opAssoc.LEFT, parse_left_associative_bin_op),
            (plusop, 2, pp.opAssoc.LEFT, parse_left_associative_bin_op),
            ((pp.Literal("<<")|pp.Literal(">>")), 2, pp.opAssoc.LEFT, parse_left_associative_bin_op),
            (pp.Literal("<=>"), 2, pp.opAssoc.LEFT, parse_left_associative_bin_op),
            (comparisons, 2, pp.opAssoc.LEFT, parse_left_associative_bin_op),
            # TODO: maybe move 'not' here like python? (with parenthesese in codegen)
            (amp_op, 2, pp.opAssoc.LEFT, parse_left_associative_bin_op),
            (pp.Literal("^"), 2, pp.opAssoc.LEFT, parse_left_associative_bin_op),
            (pp.Literal("|"), 2, pp.opAssoc.LEFT, parse_left_associative_bin_op),
            (pp.Keyword("and"), 2, pp.opAssoc.LEFT, parse_left_associative_bin_op),
            (pp.Keyword("or"), 2, pp.opAssoc.LEFT, parse_left_associative_bin_op),
            (colon, 2, pp.opAssoc.RIGHT, parse_right_associative_bin_op),
            ("=", 2, pp.opAssoc.RIGHT, parse_right_associative_bin_op),
            (pp.Keyword("return")|pp.Keyword("yield"), 1, pp.opAssoc.RIGHT, parse_right_unop),
            (ellipsis_op, 1, pp.opAssoc.LEFT, parse_left_unop),
        ],
    ).set_parse_action(_InfixExpr)

    module = pp.OneOrMore(infix_expr + block_line_end).set_parse_action(parse_module)

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
            # if op.func == "->":
            #     op = ArrowOp(op.args)
            # elif op.func == "::":
            #     op = RebuiltScopeResolution(op.func, op.args)
            pass
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