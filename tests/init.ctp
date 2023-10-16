
class (Foo:
    a : int
    def (init, x : int:
        self.a = x
    )
)

def (main:
    std.cout << Foo(5).a
)
    