# Test Output: 0121019

include <ranges>
include <algorithm>

# https://stackoverflow.com/questions/571394/how-to-find-out-if-an-item-is-present-in-a-stdvector
def (contains, container, element: const:typename:std.remove_reference_t<decltype(container)>::value_type:ref:
    unsafe.extern(std.find)
    return std.find(container.cbegin(), container.cend(), element) != container.cend()
)

def (range: template<typename:...:Args>, args: mut:Args:ref:ref:...:
    unsafe.extern(std.forward)
    if ((sizeof...)(Args) == 1:
        return std.ranges.iota_view(0, std.forward<Args>(args)...)
    else:
        return std.ranges.iota_view(std.forward<Args>(args)...)
    ) : constexpr
) : decltype(auto)

def (main:
    l = [0, 1, 2, 10, 19, 20]
    for (i in range(20):
        if (contains(l, i):
            std.cout << i
        )
    )
)
    
