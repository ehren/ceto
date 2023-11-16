# Test Output: generic yo
# Test Output: FooConcrete hi
# Test Output: generic hi
# Test Output: hey
# Test Output: generic hello
# Test Output: FooConcreteUnique yo
# Test Output: byval hello

class (FooGeneric:
    a
)
    
class (FooConcrete:
    a : string
)

class (FooGenericUnique:
    a
) : unique

class (FooConcreteUnique:
    a : string
) : unique

def (func, f:
    static_assert(std.is_const_v<std.remove_reference_t<decltype(f)>>)
    static_assert(std.is_reference_v<decltype(f)>)
    std.cout << "generic " << f.a << std.endl
)
    
def (func, f : FooConcrete:
    static_assert(std.is_const_v<std.remove_reference_t<decltype(f)>>)
    static_assert(std.is_reference_v<decltype(f)>)
    std.cout << "FooConcrete " << f.a << std.endl
)

def (func, f : FooConcreteUnique:
    # static_assert(std.is_const_v<decltype(f)>)  # TODO this and all params should still be const (at least in const by default mode...). 
    static_assert(not std.is_reference_v<decltype(f)>)
    std.cout << "FooConcreteUnique " << f.a << std.endl
)

# now raises: CodeGenError: Invalid specifier for class type (although maybe this case should be allowed)
# def (func2, f : const: FooConcreteUnique: ref:
#     static_assert(std.is_const_v<std.remove_reference_t<decltype(f)>>)
#     static_assert(std.is_reference_v<decltype(f)>)
#     std.cout << "FooConcreteUnique " << f.a << std.endl
# )

def (byval, f : auto:
    static_assert(not std.is_reference_v<decltype(f)>)  # when this is the last use, arguably bad insertion of std::move here? maybe it's expected (comment no longer relevant: we no longer apply std::move willy nilly to the last use of all vars, just those known to be :unique local/funcparm ceto class instances)
    std.cout << "byval " << f.a << "\n"
)

def (main:
    f = FooGeneric(s"yo")
    f2 = FooConcrete(s"hi")
    func(f)
    func(f2)
    func(FooGenericUnique(s"hi"))
    f3 = FooConcreteUnique(s"hey")
    f4 : mut = FooConcreteUnique(s"hello")
    # func2(std.move(f4))
    # func2(FooConcreteUnique("hello"))
    # func(f3)
    std.cout << f3.a << "\n"  # make sure the above call isn't the last use of f3...
    func(f4)
    func(FooConcreteUnique(s"yo"))
    byval(f4)
    # byval(f3)  # error call to deleted blah blah (f3 is const)
)
    