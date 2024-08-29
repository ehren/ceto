# Test Output: 1
# Test Output: 2
# Test Output: 1.5
# Test Output: 1.6

include <iostream>
include <cstdlib>

defmacro (a, a: IntegerLiteral|FloatLiteral:
    if ((i = asinstance(a, IntegerLiteral)):
        if (i.integer_string == "2":
            return quote(1)
        )
    else:
        f = asinstance(a, FloatLiteral)
        d = std.strtod(f.float_string.c_str(), nullptr)
        if (d >= 2.0 and d <= 3.0:
            suffix = quote(l)
            n = FloatLiteral(std.to_string(d - 0.5), suffix)
            return n
        )
    )

    return None
)

def (main:
    std.cout << 2 << "\n"
    std.cout << 2 + 1 << "\n"
    std.cout << 1.5 << "\n"
    std.cout << 2.5 + 0.1 << "\n" 
)
