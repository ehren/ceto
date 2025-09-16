#unsafe()  # unsafe mode bypasses 14 static_assert failures (currently)


# naming convention
# good = can't call unsafely even from unsafe block
# ok = can always call safely from 100% safe code (calling from unsafe code can result in UB)
# bad = calling from safe code can exhibit UB


include <functional>

class (Foo:
    vec: [int]

    def (ok_method: mut, x:
        self.vec.push_back(42)
        std.cout << x
    )
)

struct (FooStruct:
    foo
)

def (ok, x, foo:mut:auto:
    foo.vec.append(1)
    std.cout << x
)

def (ok2, x, foo:
    m: mut = foo
    m.vec.append(1)
    std.cout << x
)

def (ok3, x, foo_struct:
    #m: mut = foo_struct.foo  # even if this is banned
    fm: mut = foo_struct
    m: mut = fm.foo
    m.vec.append(1)
    std.cout << x
)

# note that if you had a non-owning container that allowed append/push_back this would not be safe
# but that requires cpp(mycrazylib.bad_container) to use
def (good4, v, foo_struct:
    m: mut = foo_struct.foo
    m.vec.append(1)
    std.cout << v[0]
)

def (ok5, x, v:mut:auto:ref:
    v.append(1)
    std.cout << x
)

# uses 'unsafe' unsafely
def (bad6, v, v2: mut:auto:ref:
    for (x:mut:auto:ref in v:
        ok5(unsafe(x), v2)  # UB but requires unsafe to unsafely pass x (a local ref) by ref
        break
    )
)

def (bad7, f, v2: mut:auto:ref:
    for (x:const:auto:ref in f.vec:
        v2.append(1)
        unsafe(std.cout << x)  # just mentioning a local var of ref type requires unsafe
        break
    )
)

# no need for an unsafe block to call
# this is why (due to the refcounted mutable ref semantics) any local var of raw C++ ref type (&), even if const, is unsafe to mention
def (bad8, f, f2: mut:auto:
    for (x:const:auto:ref in f.vec:
        f2.vec.append(1)
        unsafe(:
            # just mentioning a local var of ref type requires unsafe
            # (here it could result in UB / use after free)
            std.cout << x
        )
        break
    )
)

def (good9, f, f2: mut:auto:
    for (x in f.vec:  # const:auto rather than const:auto:ref by default
        f2.vec.append(1)  # this might invalidate references
        std.cout << x # but x is a copy not a reference so we're fine
        break
    )
)

def (good10, f:mut:auto, f2:mut:auto:
    for (x in f.vec:
        f2.vec.append(1)
        std.cout << x
        break  # comment out for std.terminate at runtime (only safe because of std.size checked indexing - allowed for references but only references to contiguous owning containers not e.g. span/views)
    )
)

def (mutates, f: mut:auto:
    f.vec.append(42)
)

class (HoldsFunc:
    func: std.function<void(const:int:ref)>
)

def (main:
    vec: mut = [1,2,3,4]
    f: mut = Foo(vec)
    s: mut = FooStruct(f)
    ok(f.vec[0], f)  # static_assert 1
    ok2(f.vec[0], f) # static_assert 2
    ok3(f.vec[0], s) # static_assert 3
    good4(f.vec, s)
    ok5(f.vec[0], f.vec) # static_assert 4
    bad6(f.vec, f.vec)
    f.ok_method(f.vec[0]) # static_assert 5

    bad7(f, f.vec)        # use of local ref in unsafe block in bad7 can result in UB
    bad8(f, f)            # same bad behaviour in unsafe block
    good9(f, f)  
    good10(f, f)

    ok_lambda = lambda (x:
        f_m: mut = f
        f_m.vec.append(42)
    )

    ok_lambda(f.vec[0])  # static_assert 6

    ok_lambda2 = lambda (x:
        mutates(f)
    )

    ok_lambda2(f.vec[0])  # static_assert 7

    ok_lambda3 = lambda (x, f:
        mutates(f)
    )

    ok_lambda3(f.vec[0], f) # static_assert 8

    has_ok_lambda_member1 = HoldsFunc(lambda(x:
        mutates(f)
    ))

    ok_lambda5 = lambda (x:mut:auto, f: mut:auto:
        mutates(f)
    )

    val = f.vec[0]
    has_ok_lambda_member1.func(val)  # good
    has_ok_lambda_member1.func(f.vec[0])  # static_assert 9

    ok_lambda5(val, f)
    ok_lambda5(f.vec[0], f)  # static_assert 10

    ok_func_member_copy = has_ok_lambda_member1.func
    ok_func_member_copy(f.vec[0])  # static_assert 11

    ok_lambda_like_ok5 = lambda(x, v: mut:auto:ref:
        v.append(1)
    )
    ok_lambda_like_ok5(f.vec[0], f.vec)  # static_assert 12

    bad_lambda_like_bad8 = lambda (f, f2: mut:auto:
        for (x:const:auto:ref in f.vec:
            f2.vec.append(1)
            std.cout << unsafe(x)  # potential UB if previous line resulted in relocation
            break
        )
    )

    bad_lambda_like_bad8(f, f)  # potential UB

   # std.cout << std.is_reference_v<overparenthesized_decltype(lambda[ref](vec.at(0))())>  # 0
    #std.cout << std.is_reference_v<overparenthesized_decltype(lambda[ref](vec.at(0)):decltype(auto)())>  # 1
)

