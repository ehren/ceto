

# another problem with half flattened TypeOp (previously, inside decltype, x:int is a TypeOf not an Identifier with .declared_type):
# (now works)
def (foo, f : decltype(std.function(lambda(x:int, 0))) = lambda(x:int, 0):
    return f(3)
)

# this required the logic in build_types that recurses over any nested TypeOp on rhs of operator ':' (newly added as of the commit that added this comment)
def (foo2, f : decltype(std.function(lambda(x:int, 0):int)) = lambda(x:int, 0):int:
    return f(3)
)

def (foo3, f : std.add_const_t<decltype(std.function(lambda(x:int, 0):int))> = lambda(x:int, 0):int:
    static_assert(std.is_const_v<decltype(f)>)
    return f(3)
)
    
def (main:
    l = lambda(x:int:
        std.cout << "hi" + std.to_string(x)
        5
    )
    
    f : std.function = l
    v = [f]
    std.cout << v[0](5) << "\n"
    std.cout << foo() << "\n"
    std.cout << foo(l) << "\n"
    std.cout << foo2() << "\n"
    std.cout << foo2(l) << "\n"
    std.cout << foo3() << "\n"
    std.cout << foo3(l)
)
    