include <ranges>

defmacro([x, for (y in z), if (c)], x, y, z, c:
    result_append = quote(result.append(unquote(x)))

    conditional_append = if (c.name() == "True":
        # Optimize out only an "if (True)" filter:
        # - to avoid an always true warning from C++ 
        # - more importanly to demo code sharing between macros 
        result_append
    else:
        quote(if (unquote(c):
            unquote(result_append)
        ))
    )

    return quote(lambda[ref] (:
        # TODO move gensym to ast.cth (for now rely on shadowing for hygiene)
        result: mut = []
        for (unquote(y) in unquote(z):
            unquote(conditional_append)
        )
        return result
    ) ())
)

defmacro([x, for (y in z)], x, y, z:
    # use existing def:
    return quote([unquote(x), for (unquote(y) in unquote(z)), if (True)])
)

def (main:
    l = [x, for (x in std.ranges.iota_view(0, 10)), if (x % 2 == 0)]
    for (x in l:
        std.cout << x
    )

    l2 = [x + 1, for (x in std.ranges.iota_view(0, 5))]
    #l3 = [x + 1, for (x in l)]  # should work
    #for (i in [x, for (x in l2), if (x > 5)]:
    #    std.cout << i
    #)
)
