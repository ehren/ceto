#
# Based on the pyparsing example parsePythonValue.py
#
# 
#
import sys
import pyparsing as pp

# pp.ParserElement.enable_left_recursion()  # this works but packrat is faster

pp.ParserElement.enable_packrat(2**20)

import io

from .preprocessor import preprocess
from .abstractsyntaxtree import Node, UnOp, LeftAssociativeUnOp, BinOp, TypeOp, \
    Identifier, AttributeAccess, ScopeResolution, ArrowOp, Call, ArrayAccess, \
    BracedCall, IntegerLiteral, ListLiteral, TupleLiteral, BracedLiteral, \
    Block, Module, StringLiteral, RedundantParens, Assign, Template


class ParserError(Exception):
    pass


def _parse_right_unop(s, l, t):
    source = s, l
    func = t[0][0]  # TODO should be an Identifier
    args = [t[0][1]]
    u = UnOp(func, args, source)
    return u


def _parse_left_unop(s, l, t):
    func = t[0][1]  # TODO should be an Identifier
    args = [t[0][0]]
    source = s, l
    u = LeftAssociativeUnOp(func, args, source)
    return u


def _parse_right_associative_bin_op(s, l, t):
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


def _make_scope_resolution_op(func, args, source):
    if func == ".":
        return AttributeAccess(func, args, source)
    elif func == "->":
        return ArrowOp(func, args, source)
    elif func == "::":
        return ScopeResolution(func, args, source)
    return None


def _parse_left_associative_bin_op(s, l, t):
    t = t[0]
    last_arg = t[-1]
    last_op = t[-2]
    func = last_op
    if len(t) > 3:
        beg = t[0:-2]
        args = [_parse_left_associative_bin_op(s, l, pp.ParseResults([beg])), last_arg]
    else:
        args = [t[0], last_arg]
    source = s, l

    if b := _make_scope_resolution_op(func, args, source):
        return b
    else:
        # TODO "bin_op" constructor func (taking an op string plus args) with proper subclasses for AddOp etc
        # (and make 'BinOp' effectively an abstract base class)
        return BinOp(func, args, source)


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


def _parse_maybe_scope_resolved_call_like(s, l, t):
    tokens = t.as_list()

    if len(tokens) == 2:
        func = tokens[0]
        args = tokens[1]
    else:
        assert len(tokens) > 2
        # left associative:
        func = _parse_maybe_scope_resolved_call_like(s, l, pp.ParseResults(tokens[:-1]))
        args = tokens[-1]

    source = s, l

    scope_resolve_part = args.pop()
    leading_punctuation = args.pop(0)
    end_punctuation = args.pop()
    if leading_punctuation == "(":
        assert end_punctuation == ")"
        call = Call(func, args, source)
    elif leading_punctuation == "[":
        assert end_punctuation == "]"
        call = ArrayAccess(func, args, source)
    elif leading_punctuation == "{":
        assert end_punctuation == "}"
        call = BracedCall(func, args, source)

    if scope_resolve_part:
        scope_op, scope_op_rhs = scope_resolve_part
        scope_op_args = [call, scope_op_rhs]
        return _make_scope_resolution_op(scope_op, scope_op_args, source)

    return call


def _parse_identifier(s, l, t):
    name = str(t[0])
    source = s, l
    return Identifier(name, source)


def _parse_integer_literal(s, l, t):
    integer = int(t[0])
    source = s, l
    return IntegerLiteral(integer, source)


def _parse_template(s, l, t):
    lst = t.as_list()
    func = lst[0]
    args = lst[1:]
    source = s, l
    return Template(func, args, source)


def _parse_string_literal(s, loc, tokens):
    source = s, loc
    prefix = None
    suffix = None

    if len(tokens) == 3:
        prefix, string, suffix = tokens
    elif len(tokens) == 2:
        prefix, string = tokens
        if not isinstance(string, str):
            string, suffix = prefix, string
            prefix = None
    else:
        assert len(tokens) == 1
        string = tokens[0]
    return StringLiteral(string, prefix, suffix, source)


def _make_parse_action_list_like(clazz):
    def parse_action(s, l, t):
        args = t.as_list()
        source = s, l
        return clazz(args, source)
    return parse_action


def _build_grammar():

    cvtReal = lambda toks: float(toks[0])

    # define punctuation as suppressed literals
    lparen, rparen, lbrack, rbrack, lbrace, rbrace, comma = map(
        pp.Suppress, "()[]{},"
    )

    # don't pp.Suppress these to allow post-parse array vs call detection
    lit_lparen, lit_rparen, lit_lbrack, lit_rbrack, lit_lbrace , lit_rbrace = map(
        pp.Literal, "()[]{}"
    )

    not_op = pp.Keyword("not")
    and_op = pp.Keyword("and")
    or_op = pp.Keyword("or")
    reserved_words = not_op | and_op | or_op

    integer = pp.Regex(r"[+-]?\d+").setName("integer").set_parse_action(_parse_integer_literal)
    real = pp.Regex(r"[+-]?\d+\.\d*([Ee][+-]?\d+)?").setName("real").set_parse_action(cvtReal)
    tuple_literal = pp.Forward()
    list_literal = pp.Forward()
    # dict_literal = pp.Forward()
    braced_literal = pp.Forward()
    maybe_scope_resolved_call_like = pp.Forward()
    template = pp.Forward()
    scope_resolution = pp.Forward()
    infix_expr = pp.Forward()
    ident = pp.Combine(~reserved_words + pp.Word(pp.alphas + "_", pp.alphanums + "_")).set_parse_action(_parse_identifier)

    quoted_str = (pp.Optional(ident) + pp.QuotedString("'", multiline=True, esc_char="\\").leave_whitespace() + pp.Optional(ident).leave_whitespace()).set_parse_action(_parse_string_literal)
    dblquoted_str = (pp.Optional(ident) + pp.QuotedString('"', multiline=True, esc_char="\\").leave_whitespace() + pp.Optional(ident).leave_whitespace()).set_parse_action(_parse_string_literal)

    atom = (
        dblquoted_str
        | quoted_str
        | template
        | ident
        | real
        | integer
        | list_literal
        | tuple_literal
        # | dict_literal
        | braced_literal
    )

    tuple_literal <<= (
        (lparen + pp.delimited_list(infix_expr, min=2, allow_trailing_delim=True) + rparen) |
        (lparen + pp.Optional(infix_expr) + comma + rparen) |
        (lparen + rparen)
    ).set_parse_action(_make_parse_action_list_like(TupleLiteral))

    list_literal <<= (
        lbrack + pp.Optional(pp.delimitedList(infix_expr) + pp.Optional(comma)) + rbrack
    ).set_parse_action(_make_parse_action_list_like(ListLiteral))

    bel = pp.Suppress('\x07')

    # just allow dict literals (TODO codegen) as braced_literals with all elements TypeOf ops
    # can have complex rules to disambiguate dict literal from e.g. braced literal of class constructor calls with 'type' e.g. { Foo() : mut, Bar() : mut }
    # note: direct use of std.unordered_map is possible now: m : std.unordered_map = {{0,1}, {1,2}}  # ctad ftw

    # dict_entry = pp.Group(infix_expr + bel + infix_expr)
    # dict_literal <<= (lbrace + pp.delimited_list(dict_entry, min=1, allow_trailing_delim=True) + rbrace)

    braced_literal <<= (lbrace + pp.Optional(pp.delimited_list(infix_expr)) + rbrace).set_parse_action(_make_parse_action_list_like(BracedLiteral))

    block_line_end = pp.Suppress(";")
    block = pp.Suppress(":") + bel + pp.OneOrMore(infix_expr + pp.OneOrMore(block_line_end)).set_parse_action(_make_parse_action_list_like(Block))

    template_disambig_char = pp.Suppress("\x06")
    template <<= ((ident | (lparen + infix_expr + rparen)) + pp.Suppress("<") + pp.delimitedList(infix_expr) + pp.Suppress(">") + pp.Optional(template_disambig_char)).set_parse_action(_parse_template)

    non_block_args = pp.Optional(pp.delimited_list(pp.Optional(infix_expr)))

    # no python slice syntax - but can be faked with TypeOp
    # array_access_args = lit_lbrack + infix_expr + pp.Optional(bel + infix_expr) + pp.Optional(bel + infix_expr) + lit_rbrack
    array_access_args = lit_lbrack + pp.Optional(pp.delimited_list(infix_expr)) + lit_rbrack

    braced_args = lit_lbrace + pp.Optional(pp.delimited_list(infix_expr)) + lit_rbrace

    call_args = lit_lparen + non_block_args + pp.ZeroOrMore(block + non_block_args) + lit_rparen

    dotop = pp.Literal(".")
    arrowop = pp.Literal("->")
    scopeop = pp.Literal("::")
    dotop_or_arrowop = dotop|arrowop

    scope_resolution <<= pp.infix_notation(atom|(lparen + infix_expr + rparen), [
            (scopeop, 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (dotop_or_arrowop, 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
    ])

    maybe_scope_resolved_call_like <<= (scope_resolution + pp.OneOrMore(pp.Group((call_args|array_access_args|braced_args) + pp.Group(pp.Optional((dotop_or_arrowop|scopeop) + scope_resolution))))).set_parse_action(_parse_maybe_scope_resolved_call_like)

    signop = pp.oneOf("+ -")
    multop = pp.oneOf("* / %")
    plusop = pp.oneOf("+ -")
    colon = pp.Literal(":")
    star_op = pp.Literal("*")
    amp_op = pp.Literal("&")
    ellipsis_op = pp.Literal("...")
    assign_op = pp.Literal("=")
    plus_assign_op = pp.Literal("+=")
    minus_assign_op = pp.Literal("-=")
    times_assign_op = pp.Literal("*=")
    div_assign_op = pp.Literal("/=")
    mod_assign_op = pp.Literal("%=")
    lshift_assign_op = pp.Literal("<<=")
    rshift_assign_op = pp.Literal(">>=")
    bitwise_and_assign_op = pp.Literal("&=")
    bitwise_or_assign_op = pp.Literal("|=")
    bitwise_xor_assign_op = pp.Literal("^=")

    _compar_atoms = list(map(pp.Literal, ["<=",">=", "<" , ">", "!=", "=="]))
    _compar_atoms.extend(map(pp.Keyword, ["in", "not in", "is", "is not"]))
    comparisons = _compar_atoms.pop()
    for c in _compar_atoms:
        comparisons |= c

    def andanderror(*t):
        raise ParserError("don't use '&&'. use 'and' instead.", *t)

    infix_expr <<= pp.infix_notation(
        maybe_scope_resolved_call_like|scope_resolution,
        [
            (pp.Literal("&&"), 2, pp.opAssoc.LEFT, andanderror),  # avoid interpreting a&&b as a&(&b)
            (not_op | star_op | amp_op, 1, pp.opAssoc.RIGHT, _parse_right_unop),
            # (expop, 2, pp.opAssoc.RIGHT, _parse_right_associative_bin_op),
            (signop, 1, pp.opAssoc.RIGHT, _parse_right_unop),
            (multop, 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (plusop, 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            ((pp.Literal("<<")|pp.Literal(">>")), 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (pp.Literal("<=>"), 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (comparisons, 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            # TODO: maybe move 'not' here like python? (with parenthesese in codegen)
            (amp_op, 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (pp.Literal("^"), 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (pp.Literal("|"), 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (and_op, 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (or_op, 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (colon, 2, pp.opAssoc.RIGHT, _parse_right_associative_bin_op),
            (assign_op | plus_assign_op | minus_assign_op | times_assign_op | div_assign_op | mod_assign_op | lshift_assign_op | rshift_assign_op | bitwise_and_assign_op | bitwise_or_assign_op | bitwise_xor_assign_op, 2, pp.opAssoc.RIGHT, _parse_right_associative_bin_op),
            (pp.Keyword("return") | pp.Keyword("yield"), 1, pp.opAssoc.RIGHT, _parse_right_unop),
            (ellipsis_op, 1, pp.opAssoc.LEFT, _parse_left_unop),
        ],
    ).set_parse_action(_InfixExpr)

    module = pp.OneOrMore(infix_expr + block_line_end).set_parse_action(_make_parse_action_list_like(Module))

    return module

grammar = _build_grammar()


def _parse(source: str):

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
        res = _parse(preprocessed)
    except pp.ParseException as orig:
        # try to improve upon the initial error from pyparsing (often backtracked too far to be helpful
        # especially with current "keywords as identifiers" treatment of "def", "class", "if", etc)

        sio.seek(0)
        reparse, replacements, subblocks = preprocess(sio, reparse=True)
        reparse = reparse.getvalue()

        try:
            _parse(reparse)
        except pp.ParseException:

            # if a control structure defining a block (aka call with block arg)
            # is responsible for the error find the first erroring subblock:

            for (lineno, colno), block in subblocks:
                # dedented = dedent(block)

                try:
                    # do_parse(dedented)
                    _parse(block)
                except pp.ParseException as blockerror:
                    print("blockerr")
                    blockerror._ceto_col = blockerror.col# + colno
                    blockerror._ceto_lineno =   blockerror.lineno -  1
                    raise blockerror

        # otherwise if a single line (that doesn't begin an indented block) fails to parse:

        for dummy, real in replacements.items():
            # dedented = dedent(real)
            try:
                # do_parse(dedented)
                _parse(real)
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

        if not isinstance(op, Node):
            return op

        op.args = [replacer(arg) for arg in op.args]
        op.func = replacer(op.func)
        return op

    res = replacer(res)

    print("final parse:", res)

    return res


if sys.platform != "win32":
    sys.setrecursionlimit(2**13)  # TODO we should leave this up to the user (this will overflow the python interpreter but that's better than an annoying hang in pyparsing)
else:
    _parse_orig = parse

    def parse(*args):
        result = None
        exc = None

        def doit(args):
            nonlocal result
            nonlocal exc
            try:
                result = _parse_orig(args)
            except BaseException as e:
                exc = e

        import threading
        sys.setrecursionlimit(5000)
        threading.stack_size(2**22)
        thread = threading.Thread(target=doit, args=args)
        thread.start()
        thread.join()

        if exc is not None:
            raise exc

        return result