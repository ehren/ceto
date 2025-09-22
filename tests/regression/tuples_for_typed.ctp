
cpp'
#include <ranges>
'
    
def (main:
    tuples: mut = []
    for (i in std.ranges.iota_view(0, 10):
        static_assert(std.is_same_v<decltype(i), const:int>)  # iter vars must be const val (no safe local ref vars)
        tuples.append((i, i + 1))
    )
    for ((x, y) in tuples:
        std.cout << x << y << "\n"
    )
    # blasted overparenthesized decltype((x)) not currently representable without cpp string
    # TODO don't silently omit RedundantParens parens in codegen
    for ((x, y):mut:auto:ref in tuples:
        static_assert(std.is_same_v<cpp"decltype((x))", int:ref>)
        static_assert(std.is_same_v<cpp"decltype((y))", int:ref>)
        unsafe(:
            x += 1
            y += 2
        )
    )
    for ((x, y):const in tuples:
        static_assert(std.is_same_v<decltype(x), const:int>)
        static_assert(std.is_same_v<decltype(y), const:int>)
        std.cout << x << y << "\n"
    )
    for ((x, y):mut in tuples:
        static_assert(std.is_same_v<decltype(x), int>)
        static_assert(std.is_same_v<decltype(y), int>)
    )
    
    # clang: warning: loop variable ‘<structured bindings>’ creates a copy from type ‘const std::tuple<int, int>’ [-Wrange-loop-construct]
    # it's fine
    for ((x, y):const:auto in tuples:
        static_assert(std.is_same_v<decltype(x), const:int>)
        static_assert(std.is_same_v<decltype(y), const:int>)
    )
)
    
    
