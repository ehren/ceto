
cpp'
#include <ranges>
'

def (main:
    tuples: mut = []
    for (i in std.ranges.iota_view(0, 10):
        tuples.append((i, i + 1))
    )
    for ((x, y) in tuples:
        std.cout << x << y << "\n"
    )
)
        