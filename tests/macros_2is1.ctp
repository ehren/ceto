# Test Output: 1
# Test Output: 2

include <iostream>

defmacro (a, a: IntegerLiteral:
    if (a.integer_string == "2":
        return quote(1)
    )
    return None
)

def (main:
    std.cout << 2 << "\n"
    std.cout << 2 + 1 << "\n"
)
