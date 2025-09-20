# Test Output: 02468790200400600800

include <ranges>

include (macros_list_comprehension)
#include (listcomp_simple)

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

    for (i in [x + l[0], for (x in l)]:
        std.cout << i
    )

    list_of_lists = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]

    for (i in [x, for(x in list_of_lists[0])]:
        std.cout << i
    )

    # errors due to the pass by ref to 1-arg immediately invoked lambda in non-simple (.reserve handling) listcomp impl
    # the pass by ref to a 1 arg func is only allowed so long as the func is stateless (simple function or non-capturing lambda), which fails for the below

    #for (i in [x*list_of_lists[0][0], for(x in list_of_lists[0])]:
    #    std.cout << i
    #)

    #captured = list_of_lists[0][0]
    #for (i in [x*captured, for(x in list_of_lists[0])]:
    #    std.cout << i
    #)
)
