#
# Based on the pyparsing example parsePythonValue.py
#
# 
from time import perf_counter
from io import StringIO
import sys

import pyparsing as pp

sys.setrecursionlimit(2**13)
# pp.ParserElement.enable_left_recursion()
pp.ParserElement.enable_packrat(2**20)


from abstractsyntaxtree import Node, UnOp, LeftAssociativeUnOp, BinOp, TypeOp, \
    Identifier, AttributeAccess, ScopeResolution, ArrowOp, Call, ArrayAccess, \
    BracedCall, IntegerLiteral, ListLiteral, TupleLiteral, BracedLiteral, \
    Block, Module, StringLiteral, CStringLiteral, RedundantParens, Assign, \
    Template

from indentchecker import build_blocks


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
    if name in replaced_blocks:
        block_holder = replaced_blocks[name]
        if not block_holder.parsed_node:
            print("oh noes", sys.stderr)
            sys.exit(-1)
        block_holder.parsed_node.line_col = block_holder.line_col
        return block_holder.parsed_node
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


def _make_parse_action_string_literal(clazz):
    def parse_action(s, l, t):
        func = str(t[0])
        args = []
        source = s, l
        return clazz(func, args, source)
    return parse_action


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
    ident = pp.Word(pp.alphas + "_", pp.alphanums + "_").set_parse_action(_parse_identifier)

    quoted_str = pp.QuotedString("'", multiline=True, esc_char="\\").set_parse_action(_make_parse_action_string_literal(StringLiteral))
    dblquoted_str = pp.QuotedString('"', multiline=True, esc_char="\\").set_parse_action(_make_parse_action_string_literal(StringLiteral))
    cdblquoted_str = pp.Suppress(pp.Keyword("c")) + pp.QuotedString('"', multiline=True).set_parse_action(_make_parse_action_string_literal(CStringLiteral))

    atom = (
            template
            | real
            | integer
            | cdblquoted_str
            | quoted_str
            | dblquoted_str
            | list_literal
            | tuple_literal
            # | dict_literal
            | braced_literal
            | ident
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

    # no python slice syntax for arrays planned
    # array_access_args = lit_lbrack + infix_expr + pp.Optional(bel + infix_expr) + pp.Optional(bel + infix_expr) + lit_rbrack
    array_access_args = lit_lbrack + infix_expr + lit_rbrack  # TODO could allow 0-args version for array declarations (although no reason not to use std::array - could also make a std::array like built-in using template notation that codegens as a C-style array definition)

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
            (pp.Keyword("and"), 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (pp.Keyword("or"), 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (colon, 2, pp.opAssoc.RIGHT, _parse_right_associative_bin_op),
            ("=", 2, pp.opAssoc.RIGHT, _parse_right_associative_bin_op),
            (pp.Keyword("return") | pp.Keyword("yield"), 1, pp.opAssoc.RIGHT, _parse_right_unop),
            (ellipsis_op, 1, pp.opAssoc.LEFT, _parse_left_unop),
        ],
        ).set_parse_action(_InfixExpr)

    # module = pp.OneOrMore(pp.ZeroOrMore(block_line_end) + infix_expr + pp.OneOrMore(block_line_end)).set_parse_action(_make_parse_action_list_like(Module))
    module = pp.OneOrMore(infix_expr + pp.OneOrMore(block_line_end)).set_parse_action(_make_parse_action_list_like(Module))

    return module


replaced_blocks = None


_quoted_string = pp.QuotedString('"') | pp.QuotedString("'")


def _build_elif_kludges_grammar():
    # TODO consider making "elif" "else" and "except" genuine UnOps (sometimes identifiers in the 'else' case) rather than relying on ':' ',' insertion (to make one liners more ergonomic and remove need for extra semicolon in 'elif: x:'
    patterns = [(pp.Keyword(k) + ~pp.FollowedBy(pp.Literal(":") | pp.Literal("\n"))) for k in ["elif", "except"]]
    pattern = None
    for p in patterns:
        p = p.set_parse_action(lambda t: t[0] + ":")
        if pattern is None:
            pattern = p
        pattern |= p

    # removing this "," insertion (to make one liners more ergonomic) would require making elif/else sometimes BinOps too...
    patterns = [pp.Keyword(k) for k in ["elif", "else"]]
    for p in patterns:
        p = p.set_parse_action(lambda t: "," + t[0])
        pattern |= p

    pattern = pattern.ignore(_quoted_string)
    return pattern


_grammar = _build_grammar()
_elif_kludges = _build_elif_kludges_grammar()


def _parse(source: str):
    t = perf_counter()

    source = _elif_kludges.transform_string(source)

    # print(source.replace("\x07", "!!!").replace("\x06", "&&&"))

    print(f"hacks preprocess time {perf_counter() - t}")

    res = _grammar.parseString(source, parseAll=True)

    print(f"pyparsing parse time {perf_counter() - t}")
    return res[0]


def _propagate_line_col(e, line_col):
    if not isinstance(e, Node):
        return
    if e.line_col is None:
        e.line_col = line_col
    for arg in e.args:
        _propagate_line_col(arg, line_col)
    _propagate_line_col(e.func, line_col)


def _parse_blocks(block_holder):
    for subblock in block_holder.subblocks:
        _parse_blocks(subblock)
    block_args = []
    lineno, colno = block_holder.line_col
    for line_source, line_col in block_holder.source:
        if not line_source.strip():
            continue
        expr = _parse(line_source)
        assert isinstance(expr, Module)
        _propagate_line_col(expr, line_col)
        block_args.extend(expr.args)

    block_holder.parsed_node = Module(block_args, source=None)


def parse(source: str):
    sio = StringIO(source)

    global replaced_blocks
    t = perf_counter()
    block_holder, replaced_blocks = build_blocks(sio)
    print(f"preprocess time {perf_counter() - t}")

    _parse_blocks(block_holder)
    print(f"block parse time {perf_counter() - t}")
    res = block_holder.parsed_node

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

        if isinstance(op, Block):
            if len(op.args) == 1 and isinstance(op.args[0], Module):
                # FIXME remove 'Module' entirely from pyparsing grammar
                op.args = op.args[0].args

        return op

    res = replacer(res)

    print("final parse:", res)

    return res