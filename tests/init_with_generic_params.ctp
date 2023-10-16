
class (Foo:
    x
    def (init, p:
        self.x = p
    )
)

def (main:
    std.cout << Foo(5).x
)
    