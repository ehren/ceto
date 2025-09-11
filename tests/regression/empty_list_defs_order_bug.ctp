include <ranges>
include <iostream>

cpp"
#define AUTO auto
"

def (main:
    result: mut = []
    #z: mut:auto:ref:ref = std.ranges.iota_view(0,10)
    z: mut = std.ranges.iota_view(0,10)
    #z:AUTO = std.ranges.iota_view(0,10)
    
    for (y in z:
        result.append(y)
    )

    std.cout << result.size()
)
