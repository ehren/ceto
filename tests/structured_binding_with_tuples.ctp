
    
def (main:
    (x, y) = (0, 1)
    std.cout << x
    std.cout << y
    static_assert(std.is_same_v<decltype(x), const:int>)
    static_assert(std.is_same_v<decltype(y), const:int>)
)
    