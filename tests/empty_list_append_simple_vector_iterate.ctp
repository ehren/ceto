# Test Output: 001122001122

def (main:
    v: mut = []
    v2: mut = []
    range = [0, 1, 2]
    
    for (x in range:
        v.append(x)    
    )
    
    for (x in [0, 1, 2]:
        v.append(x)    
    )
    
    for (x in v:
        v2.append(x)
        v2.append(x)
    )
    
    for (x in v2:
        std.cout << x
    )
)