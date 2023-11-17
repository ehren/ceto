# Test Output: 5A

class (Generic:
    x
)

class (GenericChild(Generic):
    def (init, x:
        super.init(x)
    )
)

def (main:
    f = Generic(5)
    f2 = GenericChild("A")
    std.cout << f.x << f2.x
)
