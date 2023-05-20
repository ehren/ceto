# based on
# https://github.com/aakash1104/IndentationChecker Written By: Aakash Prabhu, December 2016 (University of California, Davis)

import sys
from io import StringIO
 
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


def preprocess(file_object, reparse = False):
    parsing_stack = [Indent]
    is_it_a_template_stack = []

    rewritten = StringIO()
    replacements = {}
    began_indent = False

    blocks = []

    while parsing_stack:

        for line_number, line in enumerate(file_object, start=1):
            line = line.rstrip()

            if line == '':
                rewritten.write("\n")
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
                        diff -= TAB_WIDTH

                elif indent != curr:
                    raise IndentError("Indentation error. Expected: {} got: {}".format(curr, indent), line_number)

            rewritten.write("\n")
            rewritten.write(" " * indent)

            if reparse and blocks:
                blocks[-1][1] += "\n"
                blocks[-1][1] += " " * indent

            # non whitespace char handling

            line_to_write = ""
            comment_to_write = ""
            ok_to_hide = reparse and parsing_stack[-1] == Indent
            colon_eol = False

            n = -1

            while n < len(line) - 1:

                n += 1

                char = line[n]

                if (parsing_stack[-1] == SingleQuote and char != "'") or (parsing_stack[-1] == DoubleQuote and char != '"'):
                    line_to_write += char
                    if reparse and blocks:
                        blocks[-1][1] += char
                    continue

                if char == BEL:
                    raise PreprocessorError("no BEL", line_number)

                if char == "#":
                    if not reparse:
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
                                break

                if reparse and blocks:# and parsing_stack[-1] == Indent and char not in '"\'':
                    blocks[-1][1] += char

            if parsing_stack[-1] == OpenParen and colon_eol:
                parsing_stack.append(Indent)
                # block_start
                line_to_write += BEL
                began_indent = True
                ok_to_hide = False
                if reparse:
                    blocks.append([(line_number, n), "\n" * rewritten.getvalue().count("\n")])
            else:
                began_indent = False

                if parsing_stack[-1] == Indent and line_to_write.strip():
                    # block_line_end
                    line_to_write += ";"
                    while len(is_it_a_template_stack) > 0:
                        assert is_it_a_template_stack[-1] == OpenAngle
                        is_it_a_template_stack.pop()

                    if reparse and blocks:
                        blocks[-1][1] += ";"
                else:
                    ok_to_hide = False

            line_to_write += comment_to_write

            if ok_to_hide:
                d = "ceto_priv_dummy{}c{};".format(line_number, n + indent)
                rewritten.write(d)
                replacements[d] = line_to_write
            else:
                rewritten.write(line_to_write)

        if top := parsing_stack.pop() != Indent:
            # TODO states as real objects (error should point to the opening)
            raise PreprocessorError(f"EOF: expected a closing {expected_close[top]}", line_number)

    return rewritten, replacements, blocks
