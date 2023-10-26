

class (Foo: # this is the parse prob
    # x = 1
    # y = 2
    x = 0

    # def (init:
    #     printf("init\n")
    # )

    def (destruct:
        printf("dead %p\n", static_cast<const:void:ptr>(this))
    )

    def (bar:
        printf("in bar\n")
    )

    def (foo:
        printf("in foo method %p\n", static_cast<const:void:ptr>(this))

        bar()
        self.bar()
        printf("bar attribute access %d\n", self.x)
        printf("bar attribute access %d\n", x)
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
    