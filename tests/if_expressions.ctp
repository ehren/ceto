

def (main:
    x = if (1:
        [1, 2]
    else:
        [2, 1]
    )
    
    std.cout << x[0] << x[1]
    
    std.cout << if (1: 2 else: 1)
)

