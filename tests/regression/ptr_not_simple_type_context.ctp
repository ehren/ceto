unsafe.extern(printf, reinterpret_cast)

def (main:
    x = 0
    xmut : mut = 0
    y : const:int:pointer = &x
    y2 : int:pointer:mut
    y2 = &xmut
    y3 : mut:int:pointer
    y3 = &xmut
    hmm = reinterpret_cast<int:pointer>(1)
    static_cast<void>(y)
    static_cast<void>(y2)
    static_cast<void>(y3)
    static_assert(not std.is_same_v<decltype(nullptr), int:pointer>)
    printf("%p", static_cast<void:pointer>(hmm))
)
    
