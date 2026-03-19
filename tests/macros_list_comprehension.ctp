# Test Output: 0246879020040060080002468123123

include <ranges>

include (macros_list_comprehension)
# include (listcomp_simple)

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

    # this works even though list_of_lists[0] is a reference passed by ref to the lambda
    # because the one argument lambda makes no captures (is stateless)
    for (i in [x, for (x in list_of_lists[0])]:
        std.cout << i
    )

    # these next two fail with the complicated/prereserving listcom implementation (but not the simple/non-prereserving implementation)

    # even though list_of_lists[0] is passed as an arg to the lambda, using list_of_lists[0][0] means list_of_lists is also by-ref captured (immediately invoked lambdas that capture use c++ [&] ref capture)
    # for (i in [x*list_of_lists[0][0], for (x in list_of_lists[0])]:
    #     std.cout << i
    # )

    captured = list_of_lists[0][0]
    # same restriction here (any capture by the lambda prevents pass by ref of the iterable
    # for (i in [x*captured, for (x in list_of_lists[0])]:
    #    std.cout << i
    # )

    # a capture is ok here because there's no reference passed as the argument for the iterable to the lambda
    copy_of_list = list_of_lists[0]
    for (i in [x*captured, for (x in copy_of_list)]:
        std.cout << i
    )
)
