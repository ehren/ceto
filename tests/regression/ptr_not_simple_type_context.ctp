
def (main:
    x = 0
    xmut : mut = 0
    y : const:int:ptr = &x
    y2 : int:ptr:mut
    y2 = &xmut
    y3 : mut:int:ptr
    y3 = &xmut
    hmm = reinterpret_cast<int:ptr>(1)
    static_cast<void>(y)
    static_cast<void>(y2)
    static_cast<void>(y3)
    static_assert(not std.is_same_v<decltype(nullptr), int:ptr>)
    printf("%p", static_cast<void:ptr>(hmm))
)
    