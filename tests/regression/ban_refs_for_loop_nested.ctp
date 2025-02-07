unsafe()

def (bar, x, y:
    pass
)

class (Foo:
    a = [1, 2, 3]
    b = [4, 5, 6]

    def (blah: mut:
        self.a.append(1)
        self.b.append(2)
    )

    def (foo: mut:
        self.a.begin()  # error
        unsafe (:
            self.a.begin()
        )
        *unsafe(self.a.begin())  # TODO ban *

        for (x in self.a:
            bar(x, x)
            #self.blah()  # error
            #self.a  # error
            for (y in self.b:  # use of self in body of self.a loop but fine because self.b can't overlap (assuming C style union is banned)
                bar(x, y)
                #self.blah()  # error
                #self.b  # error
                #self.a  # error
            )
            std.cout << self.b[0]
        )
    )
)

def (create_foo:
    f: mut = Foo()
    return f
)

def (main:
    f: mut = Foo()
    f.foo()
    c = create_foo()
    c.foo()
)
