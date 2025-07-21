#
# Based on the pyparsing example parsePythonValue.py
#
#
import typing
import io
import sys
import os
import pathlib
import concurrent.futures
from time import perf_counter
import shutil

from .preprocessor import preprocess
from .abstractsyntaxtree import Node, UnOp, LeftAssociativeUnOp, BinOp, TypeOp, \
    Identifier, AttributeAccess, ScopeResolution, ArrowOp, BitwiseOrOp, EqualsCompareOp, Call, ArrayAccess, \
    BracedCall, IntegerLiteral, FloatLiteral, ListLiteral, TupleLiteral, BracedLiteral, \
    Block, Module, StringLiteral, RedundantParens, Assign, Template, InfixWrapper_, Source, SourceLoc

try:
    import cPyparsing as pp
    from cPyparsing import ParseException
    #pp.ParserElement.enableIncremental()
except ImportError:
    import pyparsing as pp
    from pyparsing import ParseException


pp.ParserElement.enablePackrat(None)


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
    in_op = pp.Keyword("in")
    reserved_words = not_op | and_op | or_op | in_op  # not strictly necessary but better for sanity's sake
    ident = set_parse_action(pp.Combine(~reserved_words + pp.Word(pp.alphas + "_", pp.alphanums + "_")), _parse_identifier)

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

    optional_infix = pp.Optional(infix_expr)
    optional_infix_with_optional_trailing_comma = pp.Optional(pp.delimitedList(infix_expr) + pp.Optional(comma))

    tuple_literal <<= set_parse_action(
        (lparen + infix_expr + comma + optional_infix_with_optional_trailing_comma + rparen) |
        (lparen + optional_infix + comma + rparen) |
        (lparen + rparen)
    , _make_parse_action_list_like(TupleLiteral))

    list_literal <<= set_parse_action(
        lbrack + optional_infix_with_optional_trailing_comma + rbrack,
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

    parenthesized_infix = lparen + infix_expr + rparen

    template_disambig_char = pp.Suppress("\x06")
    template <<= set_parse_action((ident | parenthesized_infix) + pp.Suppress("<") + optional_infix_csv + pp.Suppress(">") + pp.Optional(template_disambig_char), _parse_template)

    non_block_args = pp.Optional(pp.delimitedList(optional_infix))

    # no python slice syntax - but can be faked with TypeOp
    # array_access_args = lit_lbrack + infix_expr + pp.Optional(bel + infix_expr) + pp.Optional(bel + infix_expr) + lit_rbrack
    array_access_args = lit_lbrack + optional_infix_csv + lit_rbrack

    braced_args = lit_lbrace + optional_infix_csv + lit_rbrace

    call_args = lit_lparen + non_block_args + pp.ZeroOrMore(block + non_block_args) + lit_rparen

    dotop = pp.Literal(".")
    arrowop = pp.Literal("->")
    scopeop = pp.Literal("::")
    dotop_or_arrowop = dotop|arrowop

    scope_resolution <<= pp.infixNotation(non_numeric_atom|parenthesized_infix, [
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
            (signop, 1, pp.opAssoc.RIGHT, _parse_right_unop),
            (multop, 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (plusop, 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            ((pp.Literal("<<")|pp.Literal(">>")), 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (pp.Literal("<=>"), 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (comparisons, 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (amp_op, 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (pp.Literal("^"), 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (pp.Literal("|"), 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (and_op, 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (or_op, 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),
            (colon, 2, pp.opAssoc.RIGHT, _parse_right_associative_bin_op),
            (in_op, 2, pp.opAssoc.LEFT, _parse_left_associative_bin_op),  # note one must write (x in y) and (y in z) rather than x in y and y in z (which is parsed as x in (y and z))  - acceptable tradeoff to allow e.g. for (x:int in iter|std.views.drop(1)) but also allow one-liner ifs e.g. if (a and b: do_something) rather than requiring if ((a and b): do_something)
            (assign_op | plus_assign_op | minus_assign_op | times_assign_op | div_assign_op | mod_assign_op | lshift_assign_op | rshift_assign_op | bitwise_and_assign_op | bitwise_or_assign_op | bitwise_xor_assign_op, 2, pp.opAssoc.RIGHT, _parse_right_associative_bin_op),
            (pp.Keyword("return") | pp.Keyword("yield"), 1, pp.opAssoc.RIGHT, _parse_right_unop),
            (ellipsis_op, 1, pp.opAssoc.LEFT, _parse_left_unop),
        ],
    ), _parse_infix_wrapper)

    module = set_parse_action(pp.OneOrMore(infix_expr + block_line_end), _make_parse_action_list_like(Module))

    return module


class ParserError(Exception):
    pass


main_source = Source()


def _source_loc(s: str, l: int) -> SourceLoc:
    sl = SourceLoc(main_source, l)
    return sl


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
    source = _source_loc(s, l)
    func = t[0][0]  # TODO should be an Identifier
    args = [t[0][1]]
    u = UnOp(func, args, source)
    return u


def _parse_left_unop(s, l, t):
    func = t[0][1]  # TODO should be an Identifier
    args = [t[0][0]]
    source = _source_loc(s, l)
    u = LeftAssociativeUnOp(func, args, source)
    return u


def _parse_right_associative_bin_op(s, l, t):
    args = t[0][::2]
    func = t[0][1]
    source = _source_loc(s, l)

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
    source = _source_loc(s, l)

    if b := _make_scope_resolution_op(func, args, source):
        return b
    elif func == "|":
        return BitwiseOrOp(func, args, source)
    elif func == "==":
        return EqualsCompareOp(func, args, source)
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

    source = _source_loc(s, l)

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
    source = _source_loc(s, l)
    return Identifier(name, source)


def _parse_integer_literal(s, l, t):
    integer = str(t[0])
    suffix = t[1] if len(t) > 1 else None
    source = _source_loc(s, l)
    return IntegerLiteral(integer, suffix, source)


def _parse_float_literal(s, l, t):
    float_str = str(t[0])
    suffix = t[1] if len(t) > 1 else None
    source = _source_loc(s, l)
    return FloatLiteral(float_str, suffix, source)


def _parse_template(s, l, t):
    lst = t.asList()
    func = lst[0]
    args = lst[1:]
    source = _source_loc(s, l)
    return Template(func, args, source)


def _parse_string_literal(s, loc, tokens):
    source = _source_loc(s, loc)
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
        source = _source_loc(s, l)
        return clazz(args, source)
    return parse_action


def _parse_infix_wrapper(s, l, t):
    args = [t.asList()[0]]
    source = _source_loc(s, l)
    return InfixWrapper_(args, source)


def _build_elif_kludges_grammar():
    elif_kw, else_kw, except_kw = [pp.Keyword(k) for k in ["elif", "else", "except"]]

    # officially an if stmt is of the form:
    # if (condition:
    #    pass
    # elif: other_condition:
    #    pass
    # else:
    #    pass
    # )
    # but the extra ":" after "elif" is annoying and unlike python (so we'll optionally insert it for you)

    # An alternative is making "elif" "else" and "except" genuine UnOps (sometimes identifiers in the 'else' case)
    patterns = [(k + ~pp.FollowedBy(pp.Literal(":") | pp.Literal("\n"))) for k in [elif_kw, except_kw]]
    pattern = None
    for p in patterns:
        p = p.setParseAction(lambda t: t[0] + ":")
        if pattern is None:
            pattern = p
        pattern |= p

    # similarly for "if one liners"
    # e.g. if (cond: pass else: pass)
    # the official syntax is if (cond: pass, else: pass)
    # but we want a multiline if to be convertable to a one-liner simply by joining lines without inserting ","

    patterns = [elif_kw, else_kw]
    for p in patterns:
        p = p.addParseAction(lambda t: "," + t[0])
        pattern |= p

    qs = pp.QuotedString('"', multiline=True, escChar="\\") | pp.QuotedString("'", multiline=True, escChar="\\")
    pattern = pattern.ignore(qs)
    return pattern


grammar = _build_grammar()
elif_kludges = _build_elif_kludges_grammar()


def _parse_preprocessed(source: str):
    source = elif_kludges.transformString(source)

    # print(source.replace("\x07", "!!!").replace("\x06", "&&&"))

    res = grammar.parseString(source, parseAll=True)
    return res[0]


def parse_string(source: str):
    from textwrap import dedent

    source = source.replace("\\\\", "CETO_PRIVATE_ESCAPED_ESCAPED")
    source = source.replace("\\U", "CETO_PRIVATE_ESCAPED_UNICODE")
    source = source.replace("\\u", "CETO_PRIVATE_ESCAPED_UNICODE")
    sio = io.StringIO(source)
    preprocessed, _, subblocks = preprocess(sio, reparse=False)

    parsed_nodes = []

    futures = []
    results = {}

    for block in subblocks:
        block_source = block[-1]
        if not block_source.strip():
            continue
        m = _parse_preprocessed(block[1].strip())
        assert isinstance(m, Module)
        parsed_nodes.extend(m.args)

    main_source.source = source

    res = Module(parsed_nodes)

    # preprocessed = preprocessed.getvalue()
    # res = _parse_preprocessed(preprocessed)

    # try:
    #     res = _parse_preprocessed(preprocessed)
    # except pp.ParseException as orig:
    #     # try to improve upon the initial error from pyparsing (often backtracked too far to be helpful
    #     # especially with current "keywords as identifiers" treatment of "def", "class", "if", etc)
    #
    #     sio.seek(0)
    #     reparse, replacements, subblocks = preprocess(sio, reparse=True)
    #     reparse = reparse.getvalue()
    #
    #     try:
    #         _parse_preprocessed(reparse)
    #     except pp.ParseException:
    #
    #         # if a control structure defining a block (aka call with block arg)
    #         # is responsible for the error find the first erroring subblock:
    #
    #         for (lineno, colno), block in subblocks:
    #             # dedented = dedent(block)
    #
    #             try:
    #                 # do_parse(dedented)
    #                 _parse_preprocessed(block)
    #             except pp.ParseException as blockerror:
    #                 print("blockerr")
    #                 blockerror._ceto_col = blockerror.col  # + colno
    #                 blockerror._ceto_lineno = blockerror.lineno - 1
    #                 raise blockerror
    #
    #     # otherwise if a single line (that doesn't begin an indented block) fails to parse:
    #
    #     for dummy, real in replacements.items():
    #         # dedented = dedent(real)
    #         try:
    #             # do_parse(dedented)
    #             _parse_preprocessed(real)
    #         except pp.ParseException as lineerror:
    #             print("lineerr")
    #             dummy = dummy[len('ceto_priv_dummy'):-1]
    #             line, col = dummy.split("c")
    #             lineerror._ceto_col = int(col) + lineerror.col - 1
    #             # lineerror._ceto_col = lineerror.col
    #             lineerror._ceto_lineno = int(line)  # + lineerror.lineno
    #             raise lineerror
    #
    #     raise orig

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

        return op

    res = replacer(res)
    res = expand_namespace_calls(res)

    print("final parse:", res)

    return res


def expand_namespace_calls(module: Module):
    namespace_name = None
    namespace_block = []
    outer_block = []

    for node in module.args:
        if isinstance(node, Call) and node.func.name == "namespace":
            if len(node.args) == 1:
                if namespace_name:
                    raise ParserError("only 1 namespace call per file")
                namespace_name = node.args[0]
                continue

        if namespace_name:
            namespace_block.append(node)
        else:
            outer_block.append(node)

    if namespace_name:
        namespace = Call(func=Identifier("namespace"), args=[namespace_name, Block(namespace_block)])
        outer_block.append(namespace)
        module = Module(outer_block)

    return module


def parse_included_module(module: Identifier) -> typing.Tuple[str, str, Module]:
    from .compiler import cmdargs

    module_name = module.name
    maindir = os.path.dirname(os.path.realpath(cmdargs.filename))
    package_dir = os.path.dirname(__file__)
    include_dir = os.path.join(package_dir, os.pardir, "include")
    dirs = [maindir, package_dir] + cmdargs.include  # include_dir?
    cpp_module_path = None
    for dirname in dirs:
        module_path = os.path.join(dirname, module_name + ".cth")
        if os.path.isfile(module_path):
            cpp_module_path = os.path.join(dirname, module_name + ".donotedit.autogenerated.h")
            repr_path = os.path.join(dirname, module_name + "cth.donotedit.danger_passed_to_python_eval.cetorepr")
            break

    if cpp_module_path is None:
        raise ParserError("can't find .cth header for include", module)

    return module_path, cpp_module_path, _parse_maybe_cached(module_path, repr_path)


def _add_standard_lib_macro_imports(module: Module):
    from .compiler import cmdargs

    if not cmdargs:
        return

    if cmdargs._noslm:
        return

#    destination_dir = os.path.dirname(os.path.realpath(cmdargs.filename))
#    print(destination_dir)
#    print(module.source.header_file_cth)

#    package_dir = os.path.dirname(__file__)
#    include_dir = os.path.join(package_dir, os.pardir, "include")

    private_prefix = "ceto_private_"

#    for m in slm_modules:
#        orig_name = m + ".cth"
#        destination_name = private_prefix + orig_name
#        destination_path = os.path.join(destination_dir, destination_name)
#        for d in [package_dir, include_dir]:
#            orig_path = os.path.join(d, orig_name)
#            if os.path.isfile(orig_path):
#                if not os.path.isfile(destination_path) or os.path.getmtime(orig_path) > os.path.getmtime(destination_path):
#                    shutil.copyfile(orig_path, destination_path)
#                break

    builtin_modules = ["listcomp", "boundscheck", "convenience", "append_to_pushback"]

    module_names = [private_prefix + m for m in builtin_modules]

    #for name in module_names:
    #    seen_modules.add(name)

    extra_includes = [Call(func=Identifier("include"), args=[Identifier(name)]) for name in module_names]
    module.args = extra_includes + module.args


add_standard_lib_macros = True

def _parse_maybe_cached(filepath, repr_path):
    if os.path.isfile(repr_path):
        module_time = os.path.getmtime(filepath)
        repr_time = os.path.getmtime(repr_path)
        if repr_time > module_time:
            with open(repr_path) as f:
                repr_file = f.read()
            try:
                return expand_includes(eval(repr_file))
            except SyntaxError:
                pass

    with open(filepath) as f:
        source = f.read()

    parsed_module = parse_string(source)

    if add_standard_lib_macros: # and not any("ceto_private_" + m in filepath for m in slm_modules):
        _add_standard_lib_macro_imports(parsed_module)

    with open(repr_path, "w") as f:
        if hasattr(parsed_module, "ast_repr"):  # not implemented in pure python ast
            f.write(parsed_module.ast_repr())

    return expand_includes(parsed_module)


seen_modules = set()

def expand_includes(node: Module):
    def set_header_paths(node, cth_path, h_path):
        if node.source.header_file_cth:
            # avoid setting include path for nodes from a sub-include
            return
        node.source.header_file_cth = cth_path
        node.source.header_file_h = h_path
        for a in node.args:
            set_header_paths(a, cth_path, h_path)
        if node.func:
            set_header_paths(node.func, cth_path, h_path)

    while True:
        new_args = None

        for call in node.args:
            if isinstance(call, Call) and call.func.name == "include":
                if len(call.args) != 1:
                    raise ParserError("include call must have a single arg", call)
                module = call.args[0]
                if not isinstance(module, Identifier):
                    raise ParserError('module names must be valid identifiers', call)
                if module.name not in seen_modules:
                    seen_modules.add(module.name)  # self inclusion fine
                    module_path_cth, module_path_h, module_ast = parse_included_module(module)
                    call.args = [module]
                    index = node.args.index(call)
                    for a in module_ast.args:
                        set_header_paths(a, module_path_cth, module_path_h)
                    #new_args = node.args[0:index] + module_ast.args + [Call(Identifier("ceto_private_module_boundary"), []), Call(Identifier("unsafe"), [])] + node.args[index:]
                    new_args = node.args[0:index] + module_ast.args + [Call(Identifier("ceto_private_module_boundary"), [])] + node.args[index:]
                    #new_args = node.args[0:index] + module_ast.args + node.args[index:]
                    break

        if new_args:
            node.args = new_args
        else:
            break

    #node.args = [Call(Identifier("unsafe"), [])] + node.args
    return node


def parse_from_cmdargs(cmdargs):
    filename = cmdargs.filename
    dirname = os.path.dirname(os.path.realpath(cmdargs.filename))
    repr_path = os.path.join(dirname, pathlib.Path(filename).name + ".donotedit.danger_passed_to_python_eval.cetorepr")

    global add_standard_lib_macros
    add_standard_lib_macros = True

    result = _parse_maybe_cached(filename, repr_path)

    global seen_modules
    seen_modules = set()
    return result


def parse(source: str):
    global add_standard_lib_macros
    add_standard_lib_macros = False

    p = parse_string(source)
    result = expand_includes(p)
    global seen_modules
    seen_modules = set()
    return result


if sys.platform != "win32":
    sys.setrecursionlimit(2**13)  # TODO we should leave this up to the user (this will overflow the python interpreter but that's better than an annoying hang in pyparsing)
else:
    _parse_orig = parse_string

    def parse_string(*args):
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
