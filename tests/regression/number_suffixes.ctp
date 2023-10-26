def (main:
    x = 10.0
    y = 10.00l
    z = 100ULL
    w = 10.0f
    static_assert(std.is_same_v<decltype(x), const:double>)
    static_assert(std.is_same_v<decltype(y), const:long:double>)
    static_assert(std.is_same_v<decltype(z), const:unsigned:long:long>)
    static_assert(std.is_same_v<decltype(w), const:float>)
)
    
    