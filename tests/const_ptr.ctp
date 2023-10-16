

class (Foo:
    a : int
    def (method: mut:
        pass
    )
)

def (calls_method, f:
    f.method()
)

def (main:  #
    fc : const:Foo = Foo(1)
    # fc.method()  # error method not const
    # f : const = Foo(1)  # error from c++ (const alone not valid)
    f : const:auto = Foo(1) : mut  # const shared_ptr to non-const actual Foo
    # f = nullptr  # error
    static_assert(std.is_const_v<decltype(f)>)
    f.method()
    calls_method(f)
    # calls_method(fc)  # error method not const
)
    
    