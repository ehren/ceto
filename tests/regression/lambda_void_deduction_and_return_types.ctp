

def (is_void:
    pass
)

def (main:
    f = lambda(x:
        std.cout << x << std.endl
        void()  # still need this (cout not void but can't return it)
    )
    f(1)
    static_assert(std.is_same_v<decltype(f(1)), void>)
    static_assert(std.is_same_v<decltype(is_void()), void>)

    f2 = lambda(x:
        x
    )
    std.cout << f2(2) << std.endl
    static_assert(std.is_same_v<decltype(f2(2)), int>)
    
    f3 = lambda (x:
        std.cout << x << std.endl
    ) : void
    f3(3)
    static_assert(std.is_same_v<decltype(f3(3)), void>)
    
    f4 = lambda (x:
        std.cout << x << std.endl
        x
    ) : int
    std.cout << f4(4) << std.endl
    static_assert(std.is_same_v<decltype(f4(4)), int>)
    
    # still necessary to wrap in parens if immediately invoking?
    val = (lambda(x:
        x
    ) : int) (5)
    std.cout << val << std.endl
)
    