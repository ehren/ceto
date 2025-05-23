# Test Output: i'm const
# Test Output: i'm mut
# Test Output: i'm const
# Test Output: i'm const
# Test Output: i'm const
# Test Output: i'm const
# Test Output: i'm mut
# Test Output: i'm mut

class (Foo:
    x

    def (foo:
        std.cout << "i'm const\n"
    )

    def (foo: mut:
        self.x += self.x
        std.cout << "i'm mut\n"
    )
)

def (calls_foo, f:
    f.foo()  # I'm const
)

def (calls_foo_through_mut, m: mut:auto:
    m.foo()
)

def (calls_foo_through_mut_copy, f:
    m: mut = f
    m.foo()
)

def (main:
    m: mut = Foo(1)
    c = Foo("blah"s)

    c.foo()  # I'm const
    m.foo()  # I'm mut

    calls_foo(c)  # I'm const
    calls_foo(m)  # I'm const (thanks to propagate_const)

    calls_foo_through_mut(c)  # I'm const (mutable copy of variable bumps use_count but doesn't change that Foo is Foo:const (shared_ptr<const Foo>) by default
    calls_foo_through_mut_copy(c)  # I'm const (same)

    calls_foo_through_mut(m)  # I'm mut (this is reasonable - we don't want a call site mut annotation like calls_foo_through_mut(mut(m)) - too much boilerplate and mental burden just to use refcounting, more confusing than python, and makes no sense for non ceto shared classes so hinders generic code)

    calls_foo_through_mut_copy(m)  # I'm mut

    # Debatable if we should fix this last case i.e. implement "once const always const" (for shared reference types):

    #  The easiest and least intrusive way to implement this is with a call site mut annotation like above (known to be mut:Foo instance variables will be constified when appearing in subexpressions without it). Can modifications to ceto::propagate_const improve things? (don't think so). The other way is for every variable declaration and function parameter definition of generic const type (either untyped (or plain const for locals) or explicit use of const:auto / const:auto:ref), create a second variable definition auto&& x = ceto::constify(x_orig) where constify returns its input unchanged for everything except a Foo:mut which is converted to a Foo (aka Foo:const) implicitly (subsequent mut copies can be reassigned but not mutated through). Can we write constify not to hinder generic code? Also maybe complications with constructors? Also constify doesn't handle the struct holding (shared_ptr based) references case.

    # Also note these last two examples at least have mutation marked with "mut". Analyses determining if it's safe to use a range based for might still want to be interprocedural even if e.g. accessing a mut:static requires an unsafe block. propagate_const at least provides that proving foo(iter_var) doesn't mutate the iterable through iter_var only requires that foo and the transitive set of code it calls is free of the keyword "mut".
)


