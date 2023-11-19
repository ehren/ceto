# TestOutput: nullptrnullptr

# all definitions at global scope constexpr by default:
None2 = nullptr
None3: auto:const = nullptr  # even ones with an explicit 'type'

def (main:
    std.cout << None2 << None3
    
    static_assert(std.is_const_v<decltype(None2)>)
    static_assert(std.is_const_v<decltype(None3)>)
    static_assert(std.is_same_v<decltype(None2), const:std.nullptr_t>)
)
    
