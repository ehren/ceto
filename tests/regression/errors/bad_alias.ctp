#unsafe()  # unsafe mode bypasses 8 static_assert failures (currently)

class (Foo:
    vec

    def (bad_method: mut, x:
        self.vec.clear()
        self.vec.push_back(42)
        self.vec.push_back(42)
        self.vec.push_back(42)
        self.vec.push_back(42)
        self.vec.push_back(42)
        self.vec.push_back(42)
        std.cout << x
        std.cout << "\ndone bad_method\n"
    )
)

struct (FooStruct:
    foo
)

def (bad, x, foo:mut:auto:
    foo.vec.clear()
    foo.vec.push_back(1)
    foo.vec.push_back(1)
    foo.vec.push_back(1)
    foo.vec.push_back(1)
    foo.vec.push_back(1)
    foo.vec.push_back(1)
    std.cout << x
    std.cout << "\ndone bad\n"
)

def (bad2, x, foo:
    m: mut = foo
    m.vec.clear()
    m.vec.push_back(1)
    m.vec.push_back(1)
    m.vec.push_back(1)
    m.vec.push_back(1)
    m.vec.push_back(1)
    m.vec.push_back(1)
    m.vec.push_back(1)
    m.vec.push_back(1)
    std.cout << x
    std.cout << "\ndone bad2\n"
)

def (bad3, x, foo_struct:
    #m: mut = foo_struct.foo  # even if this is banned
    fm: mut = foo_struct
    m: mut = fm.foo
    m.vec.clear()
    m.vec.push_back(3)
    m.vec.push_back(3)
    m.vec.push_back(3)
    m.vec.push_back(3)
    m.vec.push_back(3)
    m.vec.push_back(3)
    m.vec.push_back(3)
    std.cout << x
    std.cout << "\ndone bad3\n"
)

def (ok4, v, foo_struct:
    fm: mut = foo_struct
    m: mut = fm.foo
    m.vec.clear()
    m.vec.push_back(1)
    m.vec.push_back(1)
    m.vec.push_back(1)
    m.vec.push_back(1)
    m.vec.push_back(1)
    m.vec.push_back(1)
    m.vec.push_back(1)
    std.cout << v.at(0)
    std.cout << "\ndone ok4\n"
)

def (bad5, x, v:mut:auto:ref:
    v.clear()
    v.push_back(1)
    v.push_back(1)
    v.push_back(1)
    v.push_back(1)
    v.push_back(1)
    v.push_back(1)
    v.push_back(1)
    v.push_back(1)
    v.push_back(1)
    v.push_back(1)
    v.push_back(1)
    std.cout << x
    std.cout << "\ndone bad5\n"
)

def (bad6, v, v2: mut:auto:ref:
    for (x:mut:auto:ref in v:  # should require unsafe
        bad5(x, v2)
        break
    )
    std.cout << "\ndone bad6\n"
)

def (bad7, f, v2: mut:auto:ref:
    for (x:const:auto:ref in f.vec:  # should require unsafe
        v2.push_back(1)
        v2.push_back(1)
        v2.push_back(1)
        v2.push_back(1)
        v2.push_back(1)
        v2.push_back(1)
        std.cout << x
        break
    )
    std.cout << "\ndone bad7\n"
)

def (bad8, f, f2: mut:auto:
    for (x:const:auto:ref in f.vec:  # should require unsafe
        f2.vec.push_back(1)
        f2.vec.push_back(1)
        f2.vec.push_back(1)
        f2.vec.push_back(1)
        f2.vec.push_back(1)
        f2.vec.push_back(1)
        std.cout << x
        break
    )
    std.cout << "\ndone bad8\n"
)

def (ok9, f, f2: mut:auto:
    for (x in f.vec:  # now const:auto rather than const:auto:ref by default
        f2.vec.push_back(1)
        f2.vec.push_back(1)
        f2.vec.push_back(1)
        f2.vec.push_back(1)
        f2.vec.push_back(1)
        f2.vec.push_back(1)
        std.cout << x
        break
    )
    std.cout << "\ndone ok9\n"
)

def (main:
    vec: mut = [1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337, 1337]
    f: mut = Foo(vec)
    s: mut = FooStruct(f)
    bad(f.vec.operator("[]")(65), f)  # static_assert in safe mode
    bad2(f.vec.at(65), f) # dito
    bad2(f.vec.operator("[]")(65), f) # dito
    bad3(f.vec.operator("[]")(65), s) # dito
    std.cout << std.endl
    ok4(f.vec, s)
    bad5(f.vec[65], f.vec)  # static_assert in safe mode results in exception in unsafe mode but ub still
    bad5(f.vec.operator("[]")(65), f.vec)  # static_assert in safe mode
    bad6(f.vec, f.vec)   # banned because bad5 banned
    f.bad_method(f.vec.operator("[]")(65))

    bad7(f, f.vec)        # allowed (currently) but violates simple param rules (no mixing mut ref with const ref) and no locals (for loop iter vars) of ref type
    bad8(f, f)            # violates no for loop iter vars of ref type (TODO error)
    ok9(f, f)  
    

   # std.cout << std.is_reference_v<overparenthesized_decltype(lambda[ref](vec.at(0))())>  # 0
    #std.cout << std.is_reference_v<overparenthesized_decltype(lambda[ref](vec.at(0)):decltype(auto)())>  # 1
)

