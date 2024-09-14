struct (Foo1:
    pass
)

struct (Foo2:
    def (destruct:virtual) = default
)

struct (Foo3:
    # this is actually defaulted like Foo2 (use pass; pass for non-defaulted but empty)
    def (destruct:virtual:
        pass
    )
)

def (main:
    static_assert(not std.has_virtual_destructor_v<Foo1>)
    static_assert(std.has_virtual_destructor_v<Foo2>)
    static_assert(std.has_virtual_destructor_v<Foo3>)
)
