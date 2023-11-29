# Test Output: 555

class (Generic:
    x
)

class (Concrete(Generic):
    def (init, x: int:
        super.init(x)
    )
)

class (Generic2(Generic):
    y
    def (init, x, y:
        self.y = y
        super.init(x)
    )
)

def (main:
    f = Generic(5)
    f2 = Generic("5")
    f3 = Generic2([5], "5")
    std.cout << f.x << f2.x << f3.x[0]
)
    
