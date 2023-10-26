

def (foo: template<typename:T, typename:Y>, 
       x: const:T:ref,
       y: const:Y:ref:
    return x + y
) : decltype(x*y)

def (foo: template<typename:T, typename:Y>, 
       x: T,
       y: const:Y:ref:
    return x + y
) : std.enable_if_t<std.is_pointer_v<T>, decltype(x)>
# ^ enable_if_t required here due to codegen trailing return type always style

def (main:
    std.cout << foo(1, 2)
    
    x = 5
    p = &x
    std.cout << *foo(p, 0)
)
    