# Test Output: 01234567890123456789-10-9-8-7-6-5-4-3-2-10123456789

include <ranges>
include <iostream>

def (range: template<typename:...:Args>, args: mut:Args:ref:ref:...:
    unsafe.extern(std.forward)
    if ((sizeof...)(Args) == 1:
        return std.ranges.iota_view(0, std.forward<Args>(args)...)
    else:
        return std.ranges.iota_view(std.forward<Args>(args)...)
    ) : constexpr
) : decltype(auto)

def (main:
    for (i in range(10):
        std.cout << i
    )
    for (i in range(0, 10):
        std.cout << i
    )
    for (i in range(-10, 10):
        std.cout << i
    )
)

