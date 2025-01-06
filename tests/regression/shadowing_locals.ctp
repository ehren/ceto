# Test Output: 2

g = 1

class (Foo:
    x = 1
    def (foo:
        x = 2
        std.cout << x
    )
)

def (main:
    # g = 5  # transpiler error. Makes sense to ban shadowing of ceto defined (always constexpr) globals. TODO ban shadowing them in function params.
    f = Foo()
    f.foo()
)
