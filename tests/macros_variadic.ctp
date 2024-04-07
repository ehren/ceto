# Test Output: 6abc50

include <ranges>
include <iostream>

defmacro (summation(args), args: [Node]:
    if (not args.size():
        return quote(0)
    )
    sum: mut = args[0]
    for (arg in args|std.views.drop(1):
        sum = quote(unquote(sum) + unquote(arg))
    )
    return sum
)

def (main:
    std.cout << summation(1, 2, 3)
    c = "c"
    std.cout << summation("a"s, "b", c) << summation(5) << summation()
)
