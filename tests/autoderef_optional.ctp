
    
def (main:
    x : std.optional<std.string> = "blah"
    xm : mut:std.optional<std.string> = "blah"
    static_assert(std.is_same_v<decltype(x), const:std.optional<std.string>>)
    static_assert(std.is_same_v<decltype(xm), std.optional<std.string>>)
    std.cout << x.size() << x.value().size() << x.value() << x.c_str() << x.value().c_str()
    std.cout << xm.size() << xm.value().size() << xm.value() << xm.c_str() << xm.value().c_str()
    
    xm = std.nullopt
    std.cout << xm.value_or("or")
)
    
    