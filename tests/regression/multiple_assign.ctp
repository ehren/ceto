
def (main:
    y : mut = 1
    x = y = 0
    std.cout << x << y
    y2 = y = x
    static_assert(std.is_same_v<decltype(y2), const:int>)
)
    