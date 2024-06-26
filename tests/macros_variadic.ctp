# Test Output: 6abc50

include <ranges>
include <iostream>

defmacro (summation(args), args: [Node]:
    if (not args.size():
        return quote(0)
    )

    if (defined(__clang__) and __clang_major__ < 16 and __APPLE__:
        sum = std.accumulate(args.cbegin() + 1, args.cend(), args[0], lambda(a, b, quote(unquote(a) + unquote(b))))
    else:
        sum: mut = args[0]
        for (arg in args|std.views.drop(1):
            sum = quote(unquote(sum) + unquote(arg))
        )
    ) : preprocessor
    return sum
)

def (main:
    std.cout << summation(1, 2, 3)
    c = "c"
    std.cout << summation("a"s, "b", c) << summation(5) << summation()
)
