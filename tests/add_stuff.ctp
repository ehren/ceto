# Test Output: adding foo and other
# Test Output: adding foo and other (in the member function)
# Test Output: adding other and foo
# Test Output: adding foo and other (in the member function)
# Test Output: adding foo and foo
# Test Output: adding foo and foo (in the member function)


class (Foo:

    def (operator("+"), foo:Foo:
        printf("adding foo and foo (in the member function)\n")
        return self
    )

    def (operator("+"), other:
        printf("adding foo and other (in the member function)\n")
        return self
    )
)

def (operator("+"), f:Foo, x:
    printf("adding foo and other\n")
    return f.operator("+")(x)
)

def (operator("+"), x, f:Foo:
    printf("adding other and foo\n")
    return f.operator("+")(x)
)

def (operator("+"), x:Foo, f:Foo:
    printf("adding foo and foo\n")
    return f.operator("+")(x)
)


def (main:
    n = 1
    k = 2

    Foo() + 1
    1 + Foo()
    Foo() + Foo()
)