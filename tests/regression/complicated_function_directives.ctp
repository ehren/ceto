
    
def (foo:static, x, y:
    return x + y
) : int

def (foo2: extern:"C",
        x: int,
        y: int:
    return x + y
) : int
    
def (main:
    std.cout << foo(1, 2) << foo2(3, 4)
)
    
    