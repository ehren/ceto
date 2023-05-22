TAB_WIDTH = 4
BEL = '\x07'

# Tokens

class Indent:
    pass


class _NeedsClose:
    def __init__(self, line_col):
        self.line_col = line_col


class OpenParen(_NeedsClose):
    pass


class SquareOpen(_NeedsClose):
    pass


class CurlyOpen(_NeedsClose):
    pass


class SingleQuote(_NeedsClose):
    pass


class DoubleQuote(_NeedsClose):
    pass


class OpenAngle(_NeedsClose):
    pass


expected_close = {OpenParen: ")", SquareOpen: "]", CurlyOpen: "}", SingleQuote: "'", DoubleQuote: '"', OpenAngle: '>'}


def current_indent(parsing_stack):
    return (len([c for c in parsing_stack if isinstance(c, Indent)]) - 1) * TAB_WIDTH


class PreprocessorError(Exception):
    def __init__(self, message, line_number):
        super().__init__("{}. Line {}.".format(message, line_number))


class IndentError(PreprocessorError):
    pass


class BlockHolder:
    def __init__(self, parent=None, line_col=(0, 0)):
        self.parent: BlockHolder = parent
        self.line_col = line_col
        self.source = [["", (0, 0)]]
        self.subblocks = []
        self.parsed_node = None

    def add_source(self, s: str, line_col, same_line=True):
        assert isinstance(s, str)
        if same_line:
            self.source[-1][0] += s
        else:
            self.source.append([s, line_col])


def build_blocks(file_object):
    parsing_stack = [Indent(line_number=1, n=0)]
    is_it_a_template_stack = []
    began_indent = False
    current_block = BlockHolder()
    replacement_blocks = {}

    while parsing_stack:

        for line_number, line in enumerate(file_object, start=1):
            line = line.rstrip()

            if line == '':
                current_block.add_source("\n", line_col=(line_number, 0))
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

            if isinstance(parsing_stack[-1], Indent) and line[0] != "#":

                if indent < curr:
                    # dedent
                    if began_indent:
                        raise IndentError("Error in what should be the first indented expression. Expected indent: {}. Got: {}".format(curr, indent), line_number)
                    diff = curr - indent
                    if diff % TAB_WIDTH != 0:
                        raise IndentError("Indentation not a multiple of {}".format(TAB_WIDTH), line_number)
                    while diff > 0:
                        if not isinstance(parsing_stack[-1], Indent):
                            raise IndentError("Too many de-indents!", line_number)
                        parsing_stack.pop()
                        current_block.parent.subblocks.append(current_block)
                        current_block = current_block.parent
                        diff -= TAB_WIDTH

                elif indent != curr:
                    raise IndentError("Indentation error. Expected: {} got: {}".format(curr, indent), line_number)

            # current_block.add_source("\n")
            current_block.add_source(" " * indent, line_col=(line_number, indent))

            # non whitespace char handling

            line_to_write = ""
            comment_to_write = ""
            ok_to_hide = isinstance(parsing_stack[-1], Indent)
            colon_eol = False

            n = -1

            while n < len(line) - 1:

                n += 1

                char = line[n]

                if (isinstance(parsing_stack[-1], SingleQuote) and char != "'") or (isinstance(parsing_stack[-1], DoubleQuote) and char != '"'):
                    line_to_write += char
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

                if not char.isspace():
                    colon_eol = char == ":"

                line_to_write += char

                if char == "(":
                    parsing_stack.append(OpenParen(line_number, n))
                elif char == "[":
                    parsing_stack.append(SquareOpen(line_number, n))
                elif char == "{":
                    parsing_stack.append(CurlyOpen(line_number, n))
                elif char in ")]}":
                    top = parsing_stack.pop()
                    if isinstance(top, OpenParen) or isinstance(top, SquareOpen) or isinstance(top, CurlyOpen):
                        expected = expected_close[top]
                        if char != expected:
                            raise PreprocessorError("Expected {} got {} ".format(expected, char), line_number)
                    elif isinstance(top, Indent):
                        raise PreprocessorError("Expected dedent got " + char, line_number)
                    else:
                        raise PreprocessorError("Unexpected state {} for close char {} ".format(top, char), line_number)
                elif char in '"\'':
                    if isinstance(parsing_stack[-1], SingleQuote) or isinstance(parsing_stack[-1], DoubleQuote):
                        parsing_stack.pop()
                    else:
                        parsing_stack.append(DoubleQuote(line_number, n) if char == '"' else SingleQuote(line_number, n))
                elif char == "<":
                    if not isinstance(parsing_stack[-1], SingleQuote) and not isinstance(parsing_stack[-1], DoubleQuote):
                        is_it_a_template_stack.append(OpenAngle(line_number, n))
                elif char == ">":
                    if not isinstance(parsing_stack[-1], SingleQuote) and not isinstance(parsing_stack[-1], DoubleQuote):
                        if len(is_it_a_template_stack) > 0:
                            assert isinstance(is_it_a_template_stack[-1], OpenAngle)
                            is_it_a_template_stack.pop()
                            for c in line[n + 1:]:
                                if c.isspace():
                                    continue
                                if c in ["(", "[", "{"]:
                                    line_to_write += "\x06"
                                break

            if isinstance(parsing_stack[-1], OpenParen) and colon_eol:
                parsing_stack.append(Indent())
                # block_start
                began_indent = True
                ok_to_hide = False
                key = f"_ceto_priv_block_{line_number}_{n}"
                line_to_write += BEL + "\n" + " " * indent + key + ";"
                current_block = BlockHolder(parent=current_block, line_col=(line_number, n))
                replacement_blocks[key] = current_block
            else:
                began_indent = False

                if isinstance(parsing_stack[-1], Indent) and line_to_write.strip():
                    # block_line_end
                    line_to_write += ";"
                    while len(is_it_a_template_stack) > 0:
                        assert isinstance(is_it_a_template_stack[-1], OpenAngle)
                        is_it_a_template_stack.pop()
                else:
                    ok_to_hide = False

            line_to_write += comment_to_write

            b = current_block.parent if began_indent else current_block
            b.add_source(line_to_write, same_line=not ok_to_hide, line_col=(line_number, indent))

        if not isinstance(top := parsing_stack.pop(), Indent):
            # TODO states as real objects (error should point to the opening)
            # raise PreprocessorError(f"EOF: expected a closing {expected_close[top]}", line_number)
            raise PreprocessorError(f"expected a closing {expected_close[top]}.", )

    return current_block, replacement_blocks
