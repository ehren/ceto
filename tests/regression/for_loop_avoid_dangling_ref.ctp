struct (Foo:
    a = [[[1, 2, 3], [1]], [[2]], [[3, 4], [5]]]

    def (foo_method:
        return self.a
    )
)

struct (Bar:
    foo = Foo()
)

def (main:
    b = Bar()

    for (i in std.vector(b.foo.a[0][0]):
        std.cout << i
    )

    for (i in b.foo.foo_method()[0][0]:
        std.cout << i
    )
)
