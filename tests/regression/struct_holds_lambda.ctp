# Test Output: 2 

class (Foo:
    func
)

struct (FooStruct:
    func
)

def (main:
    v = [1, 2, 3]

    # possible either our custom base for enable_shared_from_this templates (or enable_shared_from_this) requires Foo to be copyable
    #f = Foo(lambda[ref] (:
    #    std.cout << v[0]
    #    return
    #))
    
    f2 = Foo(1)
    static_cast<void>(f2)

    fs = FooStruct(lambda[ref] (v[1]))
    
    #f.func()
    std.cout << fs.func()
)

