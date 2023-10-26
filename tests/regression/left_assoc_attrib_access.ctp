
    
class (Foo:
    a
    b
    c
) 

# TODO: should just use auto parameters template syntax always (c++20)
# def (foo, x: auto:
#     pass
# )
    
def (main:
    f = Foo(1, 2, Foo(1, Foo(1, 2, Foo(1,2,3001)), Foo(1,2,3)))
    std.cout << f.c.b.c.c
)
    