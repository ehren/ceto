# Test Output: 1185811


# This currently requires CETO_EXPERIMENTAL_NON_NULL to be defined


class (Foo:
    x: int
)

def (main:
    f: mut: Foo|None = Foo(1)
    f = None
    std.cout << not f << (f == None) # 11
    # f.x = 5  # compile time error (f is a non-const optional Foo:const not a non-const optional Foo:mut)
    # std.cout << f.x  # std.terminate at runtime (null autoref of std.optional)
   
    f_mutable_but_not_reasignable: (Foo:mut)|None = Foo(1)

    f_mutable_but_not_reasignable2: (mut:Foo)|None = Foo(1)  # make sure no east/west mut probs
    static_assert(std.is_same_v<decltype(f_mutable_but_not_reasignable), decltype(f_mutable_but_not_reasignable2)>)

    # f_mutable_but_not_reasignable = None  # error (good - it may be optional but it's still const by default)
    # f_mutable_but_not_reasignable.x = 10  # error because of propagate const (the underlying instance is mutable but the variable is const - can't mutate through it - good)
    mut_alias: mut = f_mutable_but_not_reasignable  # create a mut variable to hold the instance
    mut_alias.x = 8  # the underlying instance is mutable and the variable is mutable too so modification is fine
    std.cout << f_mutable_but_not_reasignable.x  # 8

    f_fully_mut: mut:(Foo:mut)|None = Foo(1)
    f_fully_mut.x = 5
    std.cout << f_fully_mut.x
    f_fully_mut = None
    if (f_fully_mut:  # false
        f_fully_mut.x = 20
    )

    f_mut: mut = Foo(2)
    f_mut.x = 5
    f_mut = f_mutable_but_not_reasignable.value()  # only autoderef of attribute accesses - to get at the underlying Foo:mut you must call .value() on the optional
    # if (f_mut:  # error - f_mut is not an optional - it's a non-null instance var - can't compare it against nullptr or convert to bool
    #     pass
    # )

    unsafe.extern(std.move)
    f = std.move(f_mut)
    std.cout << f.x  # 8

    # std.cout << f_mut.x  # use after move (undefined behavior null deref - not a std.terminate); be very very careful with unsafe.extern(std.move, std.forward)

    unsafe.extern(ceto.get_underlying)
    std.cout << (ceto.get_underlying(f_mut) == nullptr)  # 1

    # conversion from raw shared_ptr
    unsafe.extern(std.shared_ptr, std.make_shared)
    raw_shared_ptr = std.shared_ptr<Foo.class>()
    # f = raw_shared_ptr  # std.terminate at runtime constructing from an empty ptr (good)
    non_empty_raw = std.make_shared<Foo.class>(1)
    f = non_empty_raw
    std.cout << f.x  # 1
)
