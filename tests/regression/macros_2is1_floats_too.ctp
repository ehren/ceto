# Test Output: 1
# Test Output: 2
# Test Output: 1.5
# Test Output: 2.1

include <iostream>
include <cstdlib>

defmacro (a, a: IntegerLiteral|FloatLiteral:

    if ((i = asinstance(a, IntegerLiteral)):
        if (i.integer_string == "2":
            return quote(1)
        )
    else:
        f = asinstance(a, FloatLiteral)
        if (f:
            d = std.strtod(f.float_string.c_str(), nullptr)
            if (d >= 2.0 and d <= 3.0:
                return quote(unquote(f) - 0.5)
            )
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
