#
# Based on the pyparsing example parsePythonValue.py
#
# 
#
import pyparsing as pp

import sys
from io import StringIO

sys.setrecursionlimit(2**13)
# pp.ParserElement.enable_left_recursion()
pp.ParserElement.enable_packrat(2**20)

import io

from preprocessor import preprocess

from abstractsyntaxtree import Node, UnOp, LeftAssociativeUnOp, BinOp, TypeOp, \
    Identifier, AttributeAccess, ScopeResolution, ArrowOp, Call, ArrayAccess, \
    BracedCall, IntegerLiteral, ListLiteral, TupleLiteral, BracedLiteral, \
    Block, Module, StringLiteral, CStringLiteral, RedundantParens, Assign, \
    Template


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



TAB_WIDTH = 4

BEL = '\x07'

# Tokens
Indent = 0
OpenParen = 1
SquareOpen = 2
CurlyOpen = 3
SingleQuote = 4
DoubleQuote = 5
OpenAngle = 6

expected_close = {OpenParen: ")", SquareOpen: "]", CurlyOpen: "}", SingleQuote: "'", DoubleQuote: '"', OpenAngle: '>'}


def current_indent(parsing_stack):
    return (parsing_stack.count(Indent) - 1) * TAB_WIDTH


def colon_replacement_char(current_state):
    if current_state in [CurlyOpen, SquareOpen]:
        # return BEL
        pass
    return ":"


class PreprocessorError(Exception):
    def __init__(self, message, line_number):
        super().__init__("{}. Line {}.".format(message, line_number))


class IndentError(PreprocessorError):
    pass


replaced_blocks = None


class BlockHolder:
    def __init__(self, parent=None, line_col=(0, 0)):
        self.parent : BlockHolder = parent
        self.line_col = line_col
        self.source = [""]
        self.subblocks = []
        self.parsed_node : Block = None

    def add_source(self, s: str, new_line=True):
        if not new_line:
            self.source[-1] += s
        else:
            self.source.append(s)


def do_parse(file_object):
    parsing_stack = [Indent]
    is_it_a_template_stack = []

    rewritten = StringIO()
    replacements = {}
    began_indent = False

    blocks = [ [(0, 0), ""] ]

    current_block = BlockHolder()
    replacement_blocks = {}

    while parsing_stack:

        for line_number, line in enumerate(file_object, start=1):
            line = line.rstrip()

            if line == '':
                blocks[-1][1] += "\n"
                # current_block.source += "\n"
                current_block.add_source("\n", new_line=False)
                continue

            # leading spaces
            indent = 0
            for c in line:
                if c == ' ':
                    indent += 1
                else:
                    break

            line = line[indent:]  # consume spaces
            curr = current_indent(parsing_stack)

            if parsing_stack[-1] == Indent and line[0] != "#":

                if indent < curr:
                    # dedent
                    if began_indent:
                        raise IndentError("Error in what should be the first indented expression. Expected indent: {}. Got: {}".format(curr, indent), line_number)
                    diff = curr - indent
                    if diff % TAB_WIDTH != 0:
                        raise IndentError("Indentation not a multible of {}".format(TAB_WIDTH), line_number)
                    while diff > 0:
                        if parsing_stack[-1] != Indent:
                            raise IndentError("Too many de-indents!", line_number)
                        parsing_stack.pop()
                        current_block.parent.subblocks.append(current_block)
                        current_block = current_block.parent
                        diff -= TAB_WIDTH

                elif indent != curr:
                    raise IndentError("Indentation error. Expected: {} got: {}".format(curr, indent), line_number)

            blocks[-1][1] += "\n"
            blocks[-1][1] += " " * indent
            # current_block.source += "\n"
            # current_block.source += " " * indent
            current_block.add_source("\n", new_line=False)
            current_block.add_source(" " * indent, new_line=False)

            # non whitespace char handling

            line_to_write = ""
            comment_to_write = ""
            ok_to_hide = parsing_stack[-1] == Indent
            colon_eol = False

            n = -1

            while n < len(line) - 1:

                n += 1

                char = line[n]

                if (parsing_stack[-1] == SingleQuote and char != "'") or (parsing_stack[-1] == DoubleQuote and char != '"'):
                    line_to_write += char
                    blocks[-1][1] += char
                    # current_block.source += char
                    continue

                if char == BEL:
                    raise PreprocessorError("no BEL", line_number)

                if char == "#":
                    if 0:
                        comment = line[n + 1:]
                        if 0 and comment:
                            comment = comment.replace('"', r'\"')
                            comment_to_write += 'ceto::comment("' + comment + '");'
                    line = line[:n]
                    break

                if char != ":":
                    c = char

                    if not char.isspace():
                        colon_eol = False
                else:
                    c = colon_replacement_char(parsing_stack[-1])
                    if not char.isspace():
                        colon_eol = True

                line_to_write += c

                if char == "(":
                    parsing_stack.append(OpenParen)
                elif char == "[":
                    parsing_stack.append(SquareOpen)
                elif char == "{":
                    parsing_stack.append(CurlyOpen)
                elif char in ")]}":
                    top = parsing_stack.pop()
                    if top in [OpenParen, SquareOpen, CurlyOpen]:
                        expected = expected_close[top]
                        if char != expected:
                            raise PreprocessorError("Expected {} got {} ".format(expected, char), line_number)
                    elif top == Indent:
                        raise PreprocessorError("Expected dedent got " + char, line_number)
                    else:
                        raise PreprocessorError("Unexpected state {} for close char {} ".format(top, char), line_number)
                elif char in '"\'':
                    if parsing_stack[-1] in [SingleQuote, DoubleQuote]:
                        parsing_stack.pop()
                    else:
                        parsing_stack.append(DoubleQuote if char == '"' else SingleQuote)
                elif char == "<":
                    if parsing_stack[-1] not in [SingleQuote, DoubleQuote]:
                        # doesn't take parenthesized identifiers into account:
                        # ident = ""
                        # for c in reversed(line[:n - 1]):
                        #     if c.isspace():
                        #         if ident:
                        #             break
                        #     else:
                        #         ident += c
                        # if ident.isidentifier():
                        #    # it's definitely a template
                        is_it_a_template_stack.append(OpenAngle)
                elif char == ">":
                    if parsing_stack[-1] not in [SingleQuote, DoubleQuote]:
                        if len(is_it_a_template_stack) > 0:
                            assert is_it_a_template_stack[-1] == OpenAngle
                            is_it_a_template_stack.pop()
                            for c in line[n + 1:]:
                                if c.isspace():
                                    continue
                                if c in ["(", "[", "{"]:
                                    line_to_write += "\x06"
                                    # current_block.source += ">\x06"
                                break

                blocks[-1][1] += char
                # current_block.source += char

            if parsing_stack[-1] == OpenParen and colon_eol:
                parsing_stack.append(Indent)
                # block_start
                # line_to_write += BEL
                began_indent = True
                ok_to_hide = False
                # blocks.append([(line_number, n), "\n" * rewritten.getvalue().count("\n")])
                blocks.append([(line_number, n), ""])
                key = f"_ceto_priv_block_{line_number}_{n}"
                line_to_write += BEL + "\n" + " " * indent + key + ";"
                # current_block.source += BEL + "\n" + " " * indent + key + ";"
                current_block = BlockHolder(parent=current_block, line_col=(line_number, n))
                replacement_blocks[key] = current_block
            else:
                began_indent = False

                if parsing_stack[-1] == Indent and line_to_write.strip():
                    # block_line_end
                    line_to_write += ";"
                    while len(is_it_a_template_stack) > 0:
                        assert is_it_a_template_stack[-1] == OpenAngle
                        is_it_a_template_stack.pop()

                    blocks[-1][1] += ";"
                    # current_block.source += ";"
                else:
                    ok_to_hide = False

            line_to_write += comment_to_write

            b = current_block.parent if began_indent else current_block

            if ok_to_hide:
                d = "ceto_priv_dummy{}c{};".format(line_number, n + indent)
                rewritten.write(d)
                replacements[d] = line_to_write
                b.add_source(line_to_write)
            else:
                rewritten.write(line_to_write)
                # b.source += line_to_write
                b.add_source(line_to_write, new_line=False)

        if top := parsing_stack.pop() != Indent:
            # TODO states as real objects (error should point to the opening)
            raise PreprocessorError(f"EOF: expected a closing {expected_close[top]}", line_number)

    print(current_block.source)
    return current_block, replacement_blocks



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


def parse_blocks(block_holder):
    for subblock in block_holder.subblocks:
        parse_blocks(subblock)
    # try:
    # s = "".join(block_holder.source)
    block_args = []
    for line in block_holder.source:
        if not line.strip():
            continue
        expr = _parse(line)
        assert isinstance(expr, Module)
        for a in expr.args:
            block_args.append(a)
        # if block_holder.parent:
        #     assert len(expr.args) == 1
        #     expr = expr.args[0]  # FIXME just remove Module from pyparsing grammar
        # block_args.append(expr)

    # module = _parse(s)
    block_holder.parsed_node = Module(block_args, source=None)
    # except Exception as e:
    #     pass
    # if block_holder.parent is None:
    #     block_holder.parsed_node = module
    # else:
    #     block_holder.p


def parse(source: str):
    from textwrap import dedent

    sio = io.StringIO(source)

    global replaced_blocks
    block_holder, replaced_blocks = do_parse(sio)
    parse_blocks(block_holder)
    res = block_holder.parsed_node

    # sio = io.StringIO(source)
    # preprocessed, _, _ = preprocess(sio, reparse=False)
    # preprocessed = preprocessed.getvalue()
    #
    # try:
    #     res = _parse(preprocessed)
    # except pp.ParseException as orig:
    #     # try to improve upon the initial error from pyparsing (often backtracked too far to be helpful
    #     # especially with current "keywords as identifiers" treatment of "def", "class", "if", etc)
    #
    #     sio.seek(0)
    #     reparse, replacements, subblocks = preprocess(sio, reparse=True)
    #     reparse = reparse.getvalue()
    #
    #     try:
    #         _parse(reparse)
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
    #                 _parse(block)
    #             except pp.ParseException as blockerror:
    #                 print("blockerr")
    #                 blockerror._ceto_col = blockerror.col# + colno
    #                 blockerror._ceto_lineno =   blockerror.lineno -  1
    #                 raise blockerror
    #
    #     # otherwise if a single line (that doesn't begin an indented block) fails to parse:
    #
    #     for dummy, real in replacements.items():
    #         # dedented = dedent(real)
    #         try:
    #             # do_parse(dedented)
    #             _parse(real)
    #         except pp.ParseException as lineerror:
    #             print("lineerr")
    #             dummy = dummy[len('ceto_priv_dummy'):-1]
    #             line, col = dummy.split("c")
    #             lineerror._ceto_col = int(col) + lineerror.col - 1
    #             # lineerror._ceto_col = lineerror.col
    #             lineerror._ceto_lineno = int(line)# + lineerror.lineno
    #             raise lineerror
    #
    #     raise orig


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