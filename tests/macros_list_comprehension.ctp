# Test Output: 02468790200400600800

include <ranges>

include (macros_list_comprehension)

def (main:
    l = [x, for (x in std.ranges.iota_view(0, 10)), if (x % 2 == 0)]

    for (x in l:
        std.cout << x
    )

    l2 = [x + 1, for (x in l)]

    for (i in [x, for (x in l2), if (x > 5)]:
        std.cout << i
    )

    for (i in [x * 100, for (x in l)]:
        std.cout << i
    )
)
