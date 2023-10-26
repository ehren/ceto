

def (main:
    b: bool = true
    b2 : bool = 1
    i : int = true
    # u : unsigned:int = i # error (narrowing)
    u2 : unsigned:int = 5
    ur : const:unsigned:int:ref = u2
    um = ur  # um now const by default
    static_assert(std.is_const_v<decltype(um)>)
    
    std.cout << b << b2 << i << u2 << ur << um
)
    