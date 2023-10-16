
    
class (Foo:
    pass
)
# f1 : mut:Foo = Foo()

def (main:
    f = Foo()
    static_assert(std.is_same_v<decltype(f), const:std.shared_ptr<const:Foo.class>>)

    f1 : mut:Foo = Foo()
    static_assert(std.is_same_v<decltype(f1), std.shared_ptr<Foo.class>>)

    f2 : mut = Foo()
    static_assert(std.is_same_v<decltype(f2), std.shared_ptr<Foo.class>>)

    f3 : mut = Foo() : const
    static_assert(std.is_same_v<decltype(f3), std.shared_ptr<const:Foo.class>>)

    f4 = Foo() : mut
    static_assert(std.is_same_v<decltype(f4), const:std.shared_ptr<Foo.class>>)

    f5 : const = Foo() : const
    static_assert(std.is_same_v<decltype(f5), const:std.shared_ptr<const:Foo.class>>)

    f6 : const = Foo()
    static_assert(std.is_same_v<decltype(f6), const:std.shared_ptr<const:Foo.class>>)

    f7 : const = Foo() : mut
    static_assert(std.is_same_v<decltype(f7), const:std.shared_ptr<Foo.class>>)

    f8 : const:Foo = Foo() : mut  # conversion
    static_assert(std.is_same_v<decltype(f8), const:std.shared_ptr<const:Foo.class>>)

    f9 : const:Foo = Foo()
    static_assert(std.is_same_v<decltype(f9), const:std.shared_ptr<const:Foo.class>>)

    f10 : const:Foo = Foo() : const
    static_assert(std.is_same_v<decltype(f10), const:std.shared_ptr<const:Foo.class>>)
    
    f11 : Foo:weak = f
    static_assert(std.is_same_v<decltype(f11), const:std.weak_ptr<const:Foo.class>>)
    
    f12 : mut:Foo:weak = f1
    static_assert(std.is_same_v<decltype(f12), std.weak_ptr<Foo.class>>)
    
    f13 : mut:weak:Foo = f1
    static_assert(std.is_same_v<decltype(f13), std.weak_ptr<Foo.class>>)
    
    f14 : const:weak:Foo = f1
    static_assert(std.is_same_v<decltype(f14), const:std.weak_ptr<const:Foo.class>>)
)
    