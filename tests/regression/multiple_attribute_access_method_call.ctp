
    
class (Foo:
    f : Foo
    def (use_count:
        return (&self)->use_count()
    )
)

class (FooList:
    l : [Foo] = []
)
    
def (main:
    f = Foo(Foo(Foo(Foo(Foo(nullptr)))))
    std.cout << f.f.f.f.f.use_count()
    
    (FooList() : mut).l.push_back(f)
    FooList().l
    # std.cout << FooList().l[0]  # exception (actually a call to .at())
    std.cout << Foo(Foo(nullptr)).f.use_count()
    std.cout << (Foo(Foo(nullptr)).f).use_count()
    FooList().l.operator("[]")(0)  # UB ! (but should compile)
    
    fl : mut = FooList()
    fl.l.push_back(f)
    std.cout << fl.l.operator("[]")(0).use_count()
)
    