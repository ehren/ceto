
class (Generic:
    x
    y : int
    z
    def (init, z, y:
        self.x = y
        self.y = 99
        self.z = z
    )
)

class (GenericChild(Generic):
    def (init, x:
        super.init(x, [1, 2, 3])
    )
)

def (main:
    g = Generic(101,-333)
    g2 = GenericChild(["x", "y", "z"])
    std.cout << g.x << g.y << g.z
    std.cout << g2.x[2] << g2.y << g2.z[1]
)
    