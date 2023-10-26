# Test Output: blahblahblahblahhiblahblahblahhiviaptr

struct (Foo:
    x : string
)

def (by_const_ref, f : Foo:  # pass by const ref
    static_assert(std.is_same_v<decltype(f), const:Foo:ref>)
    static_assert(std.is_reference_v<decltype(f)>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(f)>>)
    std.cout << f.x
)

def (by_val, f: Foo:mut:  # pass by value
    static_assert(std.is_same_v<decltype(f), Foo>)
    static_assert(not std.is_reference_v<decltype(f)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(f)>>)
    std.cout << f.x
)

def (by_const_val, f: Foo:const:  # pass by const value (TODO perhaps this should be pass by const ref instead - bit of a perf gotcha. same problem with string/std.string and [T])
    static_assert(std.is_same_v<decltype(f), const:Foo>)
    static_assert(not std.is_reference_v<decltype(f)>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(f)>>)
    std.cout << f.x
)

def (by_mut_ref, f: Foo:ref:mut:  # pass by non-const reference
    static_assert(std.is_same_v<decltype(f), Foo:ref>)
    static_assert(std.is_reference_v<decltype(f)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(f)>>)
    f.x += "hi"
    std.cout << f.x
)

def (by_ptr, f: Foo:ptr:  # TODO - our add const for function params with raw pointers should behave like the shared_ptr case. That is, this should really be a const Foo *const - we're generating a const Foo*  (not that it's recommended to use raw pointers anywhere)
    # static_assert(std.is_same_v<decltype(f), const:Foo:ptr:const>)  # TODO this should work
    static_assert(std.is_same_v<decltype(f), const:Foo:ptr>)  # TODO this is wrong
    static_assert(not std.is_reference_v<decltype(f)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(f)>>)  # TODO this is wrong
    static_assert(std.is_const_v<std.remove_reference_t<decltype(*f)>>)  # this is right at least
    std.cout << f->x
)

def (by_ptr_all_const, f: const:Foo:ptr:const:  # TODO this is what we want for Foo:ptr 
    # static_assert(std.is_same_v<decltype(f), const:Foo:ptr:const>)
    static_assert(not std.is_reference_v<decltype(f)>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(f)>>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(*f)>>)
    std.cout << f->x
)

def (by_ptr_mut, f: Foo:ptr:mut:
    static_assert(std.is_same_v<decltype(f), Foo:ptr>)
    static_assert(not std.is_reference_v<decltype(f)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(f)>>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(*f)>>)
    f->x += "viaptr"
    std.cout << f->x
)

def (main:
    f = Foo("blah")
    by_const_ref(f)
    by_val(f)
    by_const_val(f)
    fm : mut = f  # copy
    # by_mut_ref(f)  # error: binding reference of type ‘Foo&’ to ‘const Foo’ discards qualifiers
    by_mut_ref(fm)
    by_ptr(&f)
    by_ptr_all_const(&f)
    by_ptr_mut(&fm)
    
    # by_const_ref(Foo("blah") : mut)  # TODO this should be an error not a silent 'mut' strip
                                       # Foo("blah") : mut:shared or Foo("blah") : shared:mut should be allowed
)
    