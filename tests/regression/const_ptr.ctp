# Test Output: const
# Test Output: const
# Test Output: const
# Test Output: mut
# Test Output: const
# Test Output: const
# Test Output: mut
# Test Output: const


class (Foo:
    a : int
    def (method: mut:
        std.cout << "mut\n"
    )
    def (method:
        std.cout << "const\n"
    )
)

def (calls_method, f:
    f.method()  # always prints "const" (because of propagate_const)
    m: mut = f
    m.method()  # prints mut or const according to whether Foo or Foo:mut passed
)

def (main:
    fc = Foo(1)
    fc.method()  # const
    # f : const = Foo(1)  # error from c++ (const alone not valid)
    f : const:auto = Foo(1) : mut  # const shared_ptr to non-const actual Foo
    # f = nullptr  # error
    static_assert(std.is_const_v<decltype(f)>)
    f.method()  # const because of propagate_const
    calls_method(f)
    calls_method(fc)
    m: mut = f
    m2: mut = fc
    m.method()  # mut
    m2.method()  # const
)
