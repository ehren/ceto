# based on
# https://github.com/aakash1104/IndentationChecker Written By: Aakash Prabhu, December 2016 (University of California, Davis)

import sys
from io import StringIO
 
TAB_WIDTH = 4

GS = '\x1D'
RS = '\x1E'

# Tokens
Indent = 0
OpenParen = 1
SquareOpen = 2
CurlyOpen = 3
SingleQuote = 4
DoubleQuote = 5

expected_close = {OpenParen: ")", SquareOpen: "]", CurlyOpen: "}"}


def current_indent(parsing_stack):
    return (parsing_stack.count(Indent) - 1) * TAB_WIDTH


class PreprocessorError(Exception):
    def __init__(self, message, line_number):
        super().__init__("{}. Line {}.".format(message, line_number))


class IndentError(PreprocessorError):
    pass


def preprocess(file_object):
    parsing_stack = [Indent]

    rewritten = StringIO()
    began_indent = False

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

            if parsing_stack[-1] == Indent:

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

            # non whitespace char handling

            colon_to_write = False

            for n, char in enumerate(line):

                if colon_to_write:
                    rewritten.write(":")
                    colon_to_write = False

                if (parsing_stack[-1] == SingleQuote and char != "'") or (parsing_stack[-1] == DoubleQuote and char != '"'):
                    rewritten.write(char)
                    continue

                if char == "#":
                    line = line[:n]
                    break

                if char != ":":
                    rewritten.write(char)

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
                elif char == ":":
                    colon_to_write = True
                elif char in '"\'':
                    if parsing_stack[-1] in [SingleQuote, DoubleQuote]:
                        parsing_stack.pop()
                    else:
                        parsing_stack.append(DoubleQuote if char == '"' else SingleQuote)

            if parsing_stack[-1] == OpenParen and line.endswith(":"):
                parsing_stack.append(Indent)
                # block_start
                rewritten.write(GS)
                colon_to_write = False
                began_indent = True
            else:
                began_indent = False

                if parsing_stack[-1] == Indent and line.strip():
                    # block_line_end
                    rewritten.write(RS)

            if colon_to_write:
                rewritten.write(":")

        parsing_stack.pop()

    return rewritten


def run(prog):
    fo = StringIO(prog)
    rew=preprocess(fo)
    print("done debug crap")
    print(rew.getvalue())


"""

#def (foo`int, :y=2, x`(int+float), x`int+1, (:y+1)`(_ = if ), y:int
def (foo:int, y=2:int, x:int+float, x+1:int, x:int>0, e=:y+1:int>0, y:int:
    e + :a + b : symbol + type(e)
    
    e = :x + z : symbol  # invalid syntax - maybe its good

    e = x+z : symbol # valid syntax

    e = : x + 1 : symbol  # valid syntax (creation of symbolic expression "x+1" of type symbol)

    (int + float)(x+y)
    int (x, y)

    (symbol > 0):
        
    def (int(bar), (float+int)(x), x=int(y), int(z)=5
    def (bar:int, x:float+int, x:int, z=5:int:
        1
    )

    x =: x : symbol>0
    y =: y
    z =: z
    print(x+y+z)
    print(:x+y+z)

    e : a + b
    z = 5 : int
    x = x + y : int+float

)

if (x+1:
    a
elif: x+2:
    b
else:
    c
)

lambda (x: 1)  # unary : op
lambda (x:
    1
)  # special syntax for block


# no: (no autoexpansion in dictionary literals!)
{a: 1
   2
   3
c: 4
   5
   6
d: 7, e: 8, f: 9} 

"""

if __name__ == "__main__":
    prog = r"""
if (:a:
    2
1)
"""
    run(prog)

    prog = r"""
if (a:
    2
1:
    1:
    1
)
"""
    run(prog)



    prog = r"""
1+iff (a:
    (2+2)
2,
iff (b:
    def (f:
        1
    )
d),
)


    """
    run(prog)
    ee

    prog = r"""
    if (a:
        (2+2)
        2
    if (a: 1 + 2:
        2
        2
    )
    if (a:1 :1:
        1
    )
    foo (:x=1 :x=2:
        1
    )
    a
    )
    """
    try:
        run(prog)
    except err:
        print(err)
        pass
    run(prog)

    import sys
    sys.exit(0)

    prog = r"""
    if x==5:
        1: 
            1
        1
        1:
            1
        1
        1
    1
    if x == 5:
        pass

    """
    run(prog)

    prog = r"""
    def:
        e
        e
        t+1:
            1
    """
    run(prog)

    try:
        prog = r"""
    if (x==5:
    1
    )
        """
        run(prog)
    except IndentError as e:
        print("OK Expected Failure: ", e)
    else:
        assert False

