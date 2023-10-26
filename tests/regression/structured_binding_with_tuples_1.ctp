# Test Output: 0123

def (main:
    (x, y): mut = (0, 1)
    std.cout << x
    std.cout << y
    static_assert(std.is_same_v<decltype(x), int>)
    static_assert(std.is_same_v<decltype(y), int>)
    (x, y) = (2, 3)
    std.cout << x
    std.cout << y
)
