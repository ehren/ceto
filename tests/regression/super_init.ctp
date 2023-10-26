
class (Generic:
    x
)

class (GenericChild(Generic):
    def (init, x: int:
        super.init(x)
    )
)

class (GenericChild2(Generic):
    y
    def (init, p:
        self.y = p
        super.init(p)
    )
)

def (main:
    f = Generic(5)
    f2 = GenericChild(5)
    f3 = GenericChild2(5)
    std.cout << f.x << f2.x << f3.x
)
    