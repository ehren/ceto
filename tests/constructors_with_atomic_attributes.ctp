
class (Foo:
    a : std.atomic<int> = 0  # this is a test of our 'diy no narrowing conversion initialization' at class scope
)

class (Foo2:
    a : const:std.atomic<int>  # const data members are problematic but we allow it if you specify the full type (though e.g. a : const = 0 is an error)
    def (init, p:int:
        self.a = p
    )
)

def (main:
    f = Foo()
    f2 = Foo2(1)
    static_assert(not std.is_const_v<decltype(f.a)>)
    static_assert(std.is_const_v<decltype(f2.a)>)
)
    