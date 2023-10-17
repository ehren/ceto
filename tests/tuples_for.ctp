# Test Output: 01
# Test Output: 12
# Test Output: 23
# Test Output: 34
# Test Output: 45
# Test Output: 56
# Test Output: 67
# Test Output: 78
# Test Output: 89
# Test Output: 910

include <ranges>
include <iostream>

def (main:
    tuples: mut = []
    for (i in std.ranges.iota_view(0, 10):
        tuples.append((i, i + 1))
    )
    for ((x, y) in tuples:
        std.cout << x << y << "\n"
    )
)