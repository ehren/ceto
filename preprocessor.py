#!/Users/ehren/Documents/ml/env/bin/python3

import sys
from io import StringIO
 
TAB_WIDTH = 4


class ExprOpenParen:
    pass


class CallOpenParen:
    pass


class SquareOpen:
    pass


class CurlyOpen:
    pass


class SingleQuote:
    pass


class DoubleQuote:
    pass


class Indent:

    def __init__(self, indent=0):
        self.indent = indent


def current_indent(parsing_stack):
    for t in reversed(parsing_stack):
        if isinstance(t, Indent):
            indent = t.indent
            break
    return indent


class PreprocessorError(Exception):
    def __init__(self, message, line_number):
        super().__init__("{}. Line {}.".format(message, line_number))


class IndentError(PreprocessorError):
    pass


def preprocess(fileObject):
    parsing_stack = [Indent(0)]

    rewritten = StringIO()
    began_indent = False

    while parsing_stack != []:

        for line_number, line in enumerate(fileObject, start=1):
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

            line = line[indent:] # consume spaces
            curr = current_indent(parsing_stack)

            if isinstance(parsing_stack[-1], (Indent, CallOpenParen)):

                if indent < curr and isinstance(parsing_stack[-1], Indent):
                    # dedent

                    if began_indent:
                        raise IndentError("Error in what should be the first indented expression. Expected indent: {}. Got: {}".format(curr, indent), line_number)

                    diff = curr - indent

                    if diff % TAB_WIDTH != 0:
                        raise IndentError("Indentation not a multible of {}".format(TAB_WIDTH), line_number)

                    while diff > 0:
                        if not isinstance(parsing_stack[-1], Indent):
                            raise IndentError("Too many de-indents!", line_number)

                        parsing_stack.pop()
                        diff -= TAB_WIDTH

                elif indent != curr:
                    raise IndentError("Indentation error. Expected: {} got: {}".format(curr, indent), line_number)

            rewritten.write("\n")
            rewritten.write(" " * indent)

            # non whitespace char handling

            colon_to_write = False
            found_comment = False

            for n, char in enumerate(line):
                found_comment = False

                if colon_to_write:
                    rewritten.write(":")
                    colon_to_write = False

                if (isinstance(parsing_stack[-1], SingleQuote) and char != "'") or (isinstance(parsing_stack[-1], DoubleQuote) and char != '"'):
                    rewritten.write(char)
                    continue

                if char == "#":
                    found_comment = True
                    line = line[:n]
                    break

                if char != ":":
                    rewritten.write(char)

                if char == "(":
                    
                    revalue = rewritten.getvalue()
                    revalue = revalue[:-1]

                    ident = ""
                    is_ident = False
                    while revalue:
                        ident = revalue[-1] + ident
                        revalue = revalue[:-1]
                        if ident.strip().isidentifier():
                            is_ident = True
                            break
                        elif not ident.isspace():
                            break
                    if is_ident:
                        parsing_stack.append(CallOpenParen())
                    else:
                        parsing_stack.append(ExprOpenParen())
                elif char == "[":
                    parsing_stack.append(SquareOpen())
                elif char == "{":
                    parsing_stack.append(CurlyOpen())
                elif char in ")]}":
                    top = parsing_stack.pop()
                    if isinstance(top, SquareOpen):
                        if char != "]":
                            raise PreprocessorError("Expected ] got " + char, line_number)
                    elif isinstance(top, CurlyOpen):
                        if char != "}":
                            raise PreprocessorError("Expected } got " + char, line_number)
                    elif isinstance(top, (ExprOpenParen, CallOpenParen)):
                        if char != ")":
                            raise PreprocessorError("Expected ) got " + char, line_number)
                    elif isinstance(top, Indent):
                        raise PreprocessorError("Expected dedent got " + char, line_number)
                    elif not isinstance(top, (SingleQuote, DoubleQuote)):
                        raise PreprocessorError("Unexpected state {} for close char {} ".format(top, char), line_number)
                elif char == ":":
                    colon_to_write = True
                elif char in '"\'':
                    if isinstance(parsing_stack[-1], (SingleQuote, DoubleQuote)):
                        parsing_stack.pop()
                    else:
                        parsing_stack.append(DoubleQuote() if char == '"' else SingleQuote())

            #if isinstance(parsing_stack[-1], CallOpenParen) and line.endswith(":"):
            # ^ this is not the best way due to difficulty parsing indirect calls.
            # Let's just require a colon at the end of the line (within) any parentheses (type colons spilling over a line can use more parentheses e.g. "x : (
            # int)
            if isinstance(parsing_stack[-1], (ExprOpenParen, CallOpenParen)) and line.endswith(":"):
                parsing_stack.append(Indent(current_indent(parsing_stack) + TAB_WIDTH))
                # block_start
                gs = '\x1D'
                rewritten.write(gs)
                colon_to_write = False
                began_indent = True
            else:
                began_indent = False

                if isinstance(parsing_stack[-1], Indent) and line.strip():
                    # block_line_end
                    rs = '\x1E'
                    rewritten.write(rs)

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

