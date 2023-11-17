# Test Output: 123424681234123412341234


def (map, values, fun:
    results : mut = []
    for (v in values:
        results.append(fun(v))
    )
    return results
)

def (foo, x:int:
    std.cout << x
    return x
)

def (foo_generic, x:
    std.cout << x
    return x
)

def (main:
    l = [1, 2, 3, 4]
    map(map(l, lambda (x:
        std.cout << x
        x*2
    )), lambda (x:
        std.cout << x
        x
    ))
    map(l, foo)
    # map(l, foo_generic)  # error
    map(l, lambda (x:int, foo_generic(x)))  # when lambda arg is typed, clang 14 -O3 produces same code as passing foo_generic<int>)
    map(l, lambda (x, foo_generic(x)))  # Although we can trick c++ into deducing the correct type for x here clang 14 -O3 produces seemingly worse code than passing foo_generic<int> directly. 
    map(l, foo_generic<int>)  # explicit template syntax
)
	