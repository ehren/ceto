# Test Output: 25

g : const = 5  # codegen writes this as constexpr const g = 5 (TODO confirm this with a test)
def (main:
    c: const = 2
    static_assert(std.is_const_v<decltype(c)>)
    static_assert(std.is_const_v<decltype(g)>)
    std.cout << c << g
)
    