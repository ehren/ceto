# Test Output: 01
# Test Output: 12
# Test Output: 23
# Test Output: 34
# Test Output: 00
# Test Output: 56
# Test Output: 12
# Test Output: 71
# Test Output: 89
# Test Output: 910
# Test Output: 01

include <ranges>
include <iostream>

#def (foo, (x, y):   # maybe TODO
def (foo, tuple1: (int, int), tuple2 = (0, 1):
    return (std.get<0>(tuple1), std.get<1>(tuple2))
)

def (main:
    tuples: mut = []

    for (i in std.ranges.iota_view(0, 10):
        tuples.append((i, i + 1))
    )

    (a, b) = (tuples[0], tuples[1])
    tuples.append(a)

    (tuples[4], tuples[6]) = ((0, 0), b)

    (std.get<0>(tuples[7]), std.get<1>(tuples[7])) = foo(tuples[7])

    for ((x, y) in tuples:
        std.cout << x << y << "\n"
    )
)