# Test Output: bar 0
# Test Output: in == method - other not foo
# Test Output: overload == works
# Test Output: in == method - both foo
# Test Output: same
# Test Output: dead
# Test Output: dead

# just a stress test - very bad idea to overload operator("==") for class instance smart ptrs

unsafe.extern(printf)

class (Foo:
    x : int = 0

    def (bar:
        printf("bar %d\n", self.x)
    )

    def (destruct:
        printf("dead\n")
    )

    def (operator("=="), other: Foo:
        printf("in == method - both foo\n")
        return self.x == other.x
    )
    def (operator("=="), other:
        printf("in == method - other not foo\n")
        return other == 5
    )
)

def (operator("=="), f: Foo, other:
    return f.operator("==")(other)
)

def (operator("=="), f: Foo, otherfoo: Foo:
    return f.operator("==")(otherfoo)
)

def (main:
    f = Foo()
    f.bar()
    if (f == 5:
        printf("overload == works\n")
    )
    b = Foo()
    if (f == b:
        printf("same\n")
    else:
        printf("not same\n")
    )
)

