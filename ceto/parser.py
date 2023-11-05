#
# Based on the pyparsing example parsePythonValue.py
#
# 
import typing
import sys
import os

import concurrent.futures
from time import perf_counter

try:
    import cPyparsing as pp
    from cPyparsing import ParseException

    pp.ParserElement.enableIncremental()
except ImportError:
    import pyparsing as pp
    from pyparsing import ParseException


pp.ParserElement.enablePackrat(2**20)


import io

from .indent_checker import build_blocks
from .abstractsyntaxtree import Node, UnOp, LeftAssociativeUnOp, BinOp, TypeOp, \
    Identifier, AttributeAccess, ScopeResolution, ArrowOp, Call, ArrayAccess, \
    BracedCall, IntegerLiteral, FloatLiteral, ListLiteral, TupleLiteral, BracedLiteral, \
    Block, Module, StringLiteral, RedundantParens, Assign, Template, InfixWrapper_


class ParserError(Exception):
    pass


last_location = 0


def set_parse_action(element, parse_action):
    # pyparsing vs cPyparsing shim
    def pa(*args):
        global last_location
        if len(args) == 3:
            s, l, t = args
            last_location = l
        elif len(args) == 2:
            l, t = args
            last_location = l
            s = ""
        else:
            s = ""
            l = last_location
            t = args
        return parse_action(s, l, t)

    return element.setParseAction(pa)


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


def _parse_maybe_scope_resolved_call_like(s, l, t):
    tokens = t.asList()

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
            raise ParserError()
        block_holder.parsed_node.line_col = block_holder.line_col
        return block_holder.parsed_node
    source = s, l
    return Identifier(name, source)


def _parse_integer_literal(s, l, t):
    integer = str(t[0])
    suffix = t[1] if len(t) > 1 else None
    source = s, l
    return IntegerLiteral(integer, suffix, source)


def _parse_float_literal(s, l, t):
    float_str = str(t[0])
    suffix = t[1] if len(t) > 1 else None
    source = s, l
    return FloatLiteral(float_str, suffix, source)


def _parse_template(s, l, t):
    lst = t.asList()
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

    string = string.replace("CETO_PRIVATE_ESCAPED_ESCAPED", "\\")
    return StringLiteral(string, prefix, suffix, source)


def _make_parse_action_list_like(clazz):
    def parse_action(s, l, t):
        args = t.asList()
        source = s, l
        return clazz(args, source)
    return parse_action


def _parse_infix_wrapper(s, l, t):
    args = [t.asList()[0]]
    source = s, l
    return InfixWrapper_(args, source)


def _build_grammar():

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
    ident = pp.Combine(~reserved_words + pp.Word(pp.alphas + "_", pp.alphanums + "_")).setParseAction(_parse_identifier)

    integer_literal = set_parse_action(pp.Regex(r"\d+") + pp.Optional(ident).leaveWhitespace(), _parse_integer_literal)
    float_literal = set_parse_action(pp.Regex(r"\d+\.\d*") + pp.Optional(ident).leaveWhitespace(), _parse_float_literal)
    tuple_literal = pp.Forward()
    list_literal = pp.Forward()
    # dict_literal = pp.Forward()
    braced_literal = pp.Forward()
    maybe_scope_resolved_call_like = pp.Forward()
    template = pp.Forward()
    scope_resolution = pp.Forward()
    infix_expr = pp.Forward()

    quoted_str = set_parse_action(pp.Optional(ident) + pp.QuotedString("'", multiline=True, escChar="\\").leaveWhitespace() + pp.Optional(ident).leaveWhitespace(), _parse_string_literal)
    dblquoted_str = set_parse_action(pp.Optional(ident) + pp.QuotedString('"', multiline=True, escChar="\\").leaveWhitespace() + pp.Optional(ident).leaveWhitespace(), _parse_string_literal)

    non_numeric_atom = (
        dblquoted_str
        | quoted_str
        | template
        | ident
        | list_literal
        | tuple_literal
        # | dict_literal
        | braced_literal
    )

    # tuple_literal <<= (
        # (lparen + pp.delimitedList(infix_expr, min=2, allow_trailing_delim=True) + rparen) |


      # (lparen + pp.delimitedList(infix_expr) + pp.Optional(comma) + rparen) |

            # (lparen + pp.delimitedList(infix_expr) + rparen) |
        # (lparen + pp.Optional(infix_expr) + comma + rparen) |
        # (lparen + rparen)


        # lbrack + pp.Optional(pp.delimitedList(infix_expr) + pp.Optional(comma)) + rbrack

    # ).setParseAction(_make_parse_action_list_like(TupleLiteral))

    tuple_literal <<= set_parse_action(
        (lparen + infix_expr + comma + pp.Optional(pp.delimitedList(infix_expr) + pp.Optional(comma)) + rparen) |
        (lparen + pp.Optional(infix_expr) + comma + rparen) |
        (lparen + rparen)
    , _make_parse_action_list_like(TupleLiteral))
    # return (expr + ZeroOrMore(Suppress(delim) + expr)).setName(dlName)

    list_literal <<= set_parse_action(
        lbrack + pp.Optional(pp.delimitedList(infix_expr) + pp.Optional(comma)) + rbrack,
    _make_parse_action_list_like(ListLiteral))

    bel = pp.Suppress('\x07')

    # just allow dict literals (TODO codegen) as braced_literals with all elements TypeOf ops
    # can have complex rules to disambiguate dict literal from e.g. braced literal of class constructor calls with 'type' e.g. { Foo() : mut, Bar() : mut }
    # note: direct use of std.unordered_map is possible now: m : std.unordered_map = {{0,1}, {1,2}}  # ctad ftw

    # dict_entry = pp.Group(infix_expr + bel + infix_expr)
    # dict_literal <<= (lbrace + pp.delimitedList(dict_entry, min=1, allow_trailing_delim=True) + rbrace)

    optional_infix_csv = pp.Optional(pp.delimitedList(infix_expr))

    braced_literal <<= set_parse_action(lbrace + optional_infix_csv + rbrace, _make_parse_action_list_like(BracedLiteral))

    block_line_end = pp.Suppress(";")
    block = pp.Suppress(":") + bel + set_parse_action(pp.OneOrMore(infix_expr + pp.OneOrMore(block_line_end)), _make_parse_action_list_like(Block))

    template_disambig_char = pp.Suppress("\x06")
    template <<= set_parse_action((ident | (lparen + infix_expr + rparen)) + pp.Suppress("<") + optional_infix_csv + pp.Suppress(">") + pp.Optional(template_disambig_char), _parse_template)

    non_block_args = pp.Optional(pp.delimitedList(pp.Optional(infix_expr)))

    # no python slice syntax - but can be faked with TypeOp
    # array_access_args = lit_lbrack + infix_expr + pp.Optional(bel + infix_expr) + pp.Optional(bel + infix_expr) + lit_rbrack
    array_access_args = lit_lbrack + optional_infix_csv + lit_rbrack

    braced_args = lit_lbrace + optional_infix_csv + lit_rbrace

    call_args = lit_lparen + non_block_args + pp.ZeroOrMore(block + non_block_args) + lit_rparen

    dotop = pp.Literal(".")
    arrowop = pp.Literal("->")
    scopeop = pp.Literal("::")
    dotop_or_arrowop = dotop|arrowop

    scope_resolution <<= pp.infixNotation(non_numeric_atom|(lparen + infix_expr + rparen), [
    (scopeop, 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
        (dotop_or_arrowop, 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
    ])

    maybe_scope_resolved_call_like <<= set_parse_action(scope_resolution + pp.OneOrMore(pp.Group((call_args|array_access_args|braced_args) + pp.Group(pp.Optional((dotop_or_arrowop|scopeop) + scope_resolution)))), _parse_maybe_scope_resolved_call_like)

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

    ellipses_ident = set_parse_action(pp.Literal("..."), _parse_identifier)

    infix_expr <<= set_parse_action(pp.infixNotation(
        maybe_scope_resolved_call_like|scope_resolution|float_literal|integer_literal|ellipses_ident,
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
    ), _parse_infix_wrapper)

    module = set_parse_action(pp.OneOrMore(infix_expr + block_line_end), _make_parse_action_list_like(Module))

    return module

grammar = _build_grammar()




replaced_blocks = None


_quoted_string = pp.QuotedString('"') | pp.QuotedString("'")


def _build_elif_kludges_grammar():
    # TODO consider making "elif" "else" and "except" genuine UnOps (sometimes identifiers in the 'else' case) rather than relying on ':' ',' insertion (to make one liners more ergonomic and remove need for extra semicolon in 'elif: x:'
    patterns = [(pp.Keyword(k) + ~pp.FollowedBy(pp.Literal(":") | pp.Literal("\n"))) for k in ["elif", "except"]]
    pattern = None
    for p in patterns:
        p = p.setParseAction(lambda t: t[0] + ":")
        if pattern is None:
            pattern = p
        pattern |= p

    # removing this "," insertion (to make one liners more ergonomic) would require making elif/else sometimes BinOps too...
    patterns = [pp.Keyword(k) for k in ["elif", "else"]]
    for p in patterns:
        p = p.setParseAction(lambda t: "," + t[0])
        pattern |= p

    pattern = pattern.ignore(_quoted_string)
    return pattern


_grammar = _build_grammar()
_elif_kludges = _build_elif_kludges_grammar()



def _parse(source: str):
    t = perf_counter()

    source = _elif_kludges.transformString(source)

    # print(source.replace("\x07", "!!!").replace("\x06", "&&&"))

    print(f"hacks preprocess time {perf_counter() - t}")

    res = _grammar.parseString(source, parseAll=True)

    print(f"pyparsing time {perf_counter() - t}")
    return res[0]


def _propagate_line_col(e, line_col):
    if not isinstance(e, Node):
        return
    if e.line_col is None:
        e.line_col = line_col
    elif e.line_col[0] < line_col[0] or (e.line_col[0] == line_col[0] and e.line_col[1] < line_col[1]):
        print("hmm")
    for arg in e.args:
        _propagate_line_col(arg, line_col)
    _propagate_line_col(e.func, line_col)


def thread_parse(line_source, line_col, index):
    expr = _parse(line_source)
    assert isinstance(expr, Module)
    _propagate_line_col(expr, line_col)
    return expr, index


def _parse_blocks(block_holder):
    for subblock in block_holder.subblocks:
        _parse_blocks(subblock)
    block_args = []
    # lineno, colno = block_holder.line_col
    futures = []
    results = {}

    if False and len(block_holder.source) > 24:
        # process in parallel

        with concurrent.futures.ProcessPoolExecutor() as executor:
            for index, (line_source, line_col) in enumerate(block_holder.source):
                if not line_source.strip():
                    continue
                futures.append(executor.submit(thread_parse, line_source, line_col, index))

            for future in concurrent.futures.as_completed(futures):
                expr, index = future.result()
                results[index] = expr

        # FIXME possible to use .map instead of .as_completed to avoid this?
        for k in sorted(results.keys()):
            expr = results[k]
            assert isinstance(expr, Module)
            block_args.extend(expr.args)
    else:
        # single process faster for a handful of lines

        for line_source, line_col in block_holder.source:
            if not line_source.strip():
                continue
            expr = _parse(line_source)
            assert isinstance(expr, Module)
            _propagate_line_col(expr, line_col)
            block_args.extend(expr.args)

    block_holder.parsed_node = Module(block_args)





# TODO this will probably need a -I like include path mechanism in the future
def parse_include(module: Identifier) -> typing.Tuple[str, Module]:
    from .compiler import cmdargs

    module_name = module.name

    dirname = os.path.dirname(os.path.realpath(cmdargs.filename))
    module_path = os.path.join(dirname, module_name + ".cth")

    with open(module_path) as f:
        source = f.read()

    return parse(source)


seen_modules = set()


def parse(source: str):
    from textwrap import dedent

    source = source.replace("\\\\", "CETO_PRIVATE_ESCAPED_ESCAPED")
    source = source.replace("\\U", "CETO_PRIVATE_ESCAPED_UNICODE")
    source = source.replace("\\u", "CETO_PRIVATE_ESCAPED_UNICODE")
    sio = io.StringIO(source)

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

        if isinstance(op, InfixWrapper_):
            if isinstance(op.args[0], InfixWrapper_):
                op = RedundantParens([op.args[0].args[0]], op.args[0].source)
            else:
                op = op.args[0]

        if not isinstance(op, Node):
            return op

        op.args = [replacer(arg) for arg in op.args]
        op.func = replacer(op.func)

        if isinstance(op, Block) and len(op.args) == 1 and isinstance(op.args[0], Module):
            # FIXME remove 'Module' entirely from pyparsing grammar
            op.args = op.args[0].args

        return op

    res = replacer(res)

    def set_from_include(node):
        if not isinstance(node, Node):
            return
        node.from_include = True
        for a in node.args:
            set_from_include(a)
        set_from_include(node.func)

    while True:
        new_args = None

        for call in res.args:
            if isinstance(call, Call) and call.func.name == "include":
                if len(call.args) != 1:
                    raise ParserError("include call must have a single arg", call)
                module = call.args[0]
                if not isinstance(module, Identifier):
                    raise ParserError('module names must be valid identifiers', call)
                if module.name not in seen_modules:
                    module_ast = parse_include(module)
                    # call.args = [module, module_ast]
                    call.args = [module]
                    # if not isinstance(call.parent, Module):  # TODO validate elsewhere
                    #    raise SemanticAnalysisError("unexpected location for include (must be at module level)", call)
                    index = res.args.index(call)
                    # this is crappy but avoids needing to move ClassDefinition handling out of codegen (even though that should still happen)
                    for a in module_ast.args:
                        set_from_include(a)
                    new_args = res.args[0:index] + module_ast.args + res.args[index:]
                    seen_modules.add(module.name)
                    break

        if new_args:
            res.args = new_args
        else:
            break

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