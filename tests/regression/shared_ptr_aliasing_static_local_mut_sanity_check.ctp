
class (Foo:
    def (method:
        std.cout << "method"
    )

    def (destruct:
        std.cout << "Foo destruct"
    )
)
    
class (Holder:
    f : Foo
)

def (accessor:
    # Allowing Holder to be mut because lhs has mut is a bit dubious when lhs also has explicit 'auto'
    g : mut:static:auto = Holder(nullptr)  # TODO we don't support the arguably more sensible 'static:mut:auto' (fine for now)
    
    return g
)

def (aliaser, f:
    unsafe()
    g: mut = accessor()
    g.f = nullptr
    # f.method()  # this would raise (good)
    std.cout << (f == nullptr)  # true - still safe at this point (reference lifetime extension for the shared_ptr itself (not what it's pointing to) to then end of main). no different than passing 'int' by const ref
    #std.cout << (&f)->use_count()  # 0 # no longer compiles since propagate_const changes
    std.cout << (&ceto.get_underlying(f))->use_count()  # 0
    std.cout << ((&f)->get() == nullptr) # 1 (note that our (and experimentals) propagate_const has a custom passthrough for get())
)

def (main:
    unsafe()
    f: mut = accessor()
    f.f = Foo()  # + 1
    std.cout << (&ceto.get_underlying(f.f))->use_count()
    aliaser(f.f) # + 0  (passed by const ref...)
)
    
    
