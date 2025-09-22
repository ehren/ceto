class (Foo:
    vec
)

struct (FooStruct:
    foo
)

# variation of bad7 from bad_alias.ctp

# error: static_assert(std::is_fundamental_v<decltype(f)>, "you cannot use the mut:ref param v2 (outside of an unsafe block) together with other non-fundamental (maybe reference/pointer holding) params");
def (bad7, f, v2: mut:auto:ref:
    for (x:const:auto:ref in f.vec:
        v2.push_back(1)  # TODO this should be acceptable in an unsafe block (correctly results in static_assert outside of one)
        unsafe(std.cout << x)  # using a local var of ref type (including an iter var) requires unsafe
        break
    )
    std.cout << "\ndone bad7\n"
)

# error: static_assert(std::is_fundamental_v<decltype(f)>, "you cannot use the mut:ref param v2 (outside of an unsafe block) together with other non-fundamental (maybe reference/pointer holding) params");
def (bad7_explicit, f:const:auto:ref, v2: mut:auto:ref:
    for (x:const:auto:ref in f.vec:
        v2.push_back(1)  # TODO this should be acceptable in an unsafe block (correctly results in static_assert outside of one)
        unsafe(std.cout << x)  # using a local var of ref type (including an iter var) requires unsafe
        break
    )
    std.cout << "\ndone bad7_explicit\n"
)

#def (bad, m:mut:auto:ref, c:
#    for (i in m:
#        
#    )
#)

def (main:
    vec: mut = [1,2,3,4]
    f: mut = Foo(vec)
    s: mut = FooStruct(f)

    bad7(f, f.vec)
    bad7_explicit(f, f.vec)
)

