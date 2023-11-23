include <iostream>

defmacro(x + 2 + 3, x: BinOp:
    return quote(unquote(x)*100)
)

def (main:
    y = 10
    std.cout << -5 + y + 1 + 2 + 3
)
