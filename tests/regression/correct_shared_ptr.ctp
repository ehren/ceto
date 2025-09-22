unsafe.extern (static_cast, printf)

class (Foo: # this is the parse prob
    # x = 1
    # y = 2
    x = 0

    # def (init:
    #     printf("init\n")
    # )

    def (destruct:
        printf("dead %p\n", static_cast<const:void:pointer>(this))
    )

    def (bar:
        printf("in bar\n")
    )

    def (foo:
        printf("in foo method %p\n", static_cast<const:void:pointer>(this))

        bar()  # should be disallowed but needs call-def lookup (not just "is it a class?")
        self.bar()
        printf("bar attribute access %d\n", self.x)
        # shared_from_base()
        return self
    )
)


def (calls_foo, x:
    x.foo()
    return x
)


def (main:
    # printf("hi")
    # x = 1
    # printf("%d", x)
    Foo().foo()
    f : mut = Foo()
    f.foo()
    f.x = 55
    f.foo()
    y = Foo()
    calls_foo(y).foo().foo()
)
    
