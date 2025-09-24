include <array>
    
def (main:
    a = std.array<int, 3> {1,2,3}
    a3 : std.array<int, 3> = {1,2,3}
    a4 : std.array<int, 3> = std.array<int, 3> {1,2,3}
    
    v = std.vector<int> {1,2}
    v2 = std.vector<int> (30, 5)
    v3 : std.vector<int> = {30, 5}
    
    for (x in {a, a3, a4}:
        for (i in x:
            std.cout << i
        )
    )
    
    for (x in {v, v2, v3}:
        for (i in x:
            std.cout << i
        )
    )
    
    for (x in std.array { a, a3, a4 }:
        for (i in x:
            std.cout << i
        )
    )
    
    get = lambda(t, std.cout << std.get<0>(t)[0]): void
    
    t = std.tuple {a, a3, a4, v, v2, v3}
    t2 = std.make_tuple(a,v)
    
    get(t)
    get(t2)
)
