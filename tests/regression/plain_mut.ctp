def (foo, x: mut, y:mut = 10:
    std.cout << x << y
)

def (main:
    foo(1)

    for (x:mut in [0, 1, 2]:
        static_assert(std.is_same_v<decltype(x), int>)
    )
)
