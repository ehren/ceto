
def (main:
    x : const:auto:ref = 1
    y : const:int:ref = x
    # z : auto:ref = y  # error: you must specify mut/const
    z : auto:const:ref = y
    static_assert(std.is_reference_v<decltype(x)>)
    static_assert(std.is_reference_v<decltype(y)>)
    static_assert(std.is_reference_v<decltype(z)>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(x)>>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(y)>>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(z)>>)
)
    
