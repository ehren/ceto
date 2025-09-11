include <map>

class (Foo:
    x
)

def (main:
    # with macro:
    map: std.unordered_map = { 1: [Foo(1), Foo(2)], 2: [Foo(3)] }
    for ((key, vec) in map:
        std.cout << key << std.endl
        #
        #for (foo in vec:
        #    std.cout << foo.x
        #)
    )

    # without macro:
    map2 = std.optional<std.map<int,int>> {}
    if (map2:
        std.cout << map2.at(42)  # std.optional autoderef  
    )
)
