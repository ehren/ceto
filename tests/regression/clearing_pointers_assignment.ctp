# Test Output: foo
# Test Output: foo
# Test Output: 2
# Test Output: 2
# Test Output: f 1
# Test Output: f2 1
# Test Output: 0
# Test Output: 0
# Test Output: foo
# Test Output: foo


class (Foo:
    def (foo:
        printf("foo
")
        return 5
    )
)

def (main:
    f : mut = Foo()
    f.foo()
    f2 : mut = f
    f2.foo()
    std.cout << (&f)->use_count() << std.endl
    std.cout << (&f2)->use_count() << std.endl
    f2 = nullptr
    f = nullptr
    printf("f %d
", not f)
    printf("f2 %d
", not f2)
    std.cout << (&f)->use_count() << std.endl
    std.cout << (&f2)->use_count() << std.endl
    # f.foo()  # std::terminate
    # f2.foo() # std::terminate
    f->foo()  # intentional UB
    f2->foo()  # UB
)
    