
class (Foo:
    x : int
    y : int
    # ^ these can't be generic for now (because constructor params are typed from the decltype of default argument...)
    def (init, x = 5, y = 4:
        self.x = x
        self.y = y
    )
)

def (main:
    f1 = Foo()
    f2 = Foo(1)
    f3 = Foo(2, 3)
    
    for (f in {f1, f2, f3}:
        std.cout << f.x << f.y
    )
)
    