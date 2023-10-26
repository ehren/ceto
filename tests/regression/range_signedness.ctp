
    
def (main:
    for (i in range(10):
        static_assert(std.is_same_v<decltype(i), int>)
        std.cout << i
    )
    u : unsigned:int = 10
    # for (i in range(u):  # TODO probably should fix
    z : unsigned:int = 0  # workaround
    for (i in range(z, u):
        static_assert(std.is_same_v<decltype(i), int:unsigned>)
        static_assert(std.is_same_v<decltype(i), unsigned:int>)
        std.cout << i
    )
)

    