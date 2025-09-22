# Test Output: adding foo and other
# Test Output: adding foo and other (in the member function)
# Test Output: done
# Test Output: adding other and foo
# Test Output: adding foo and other (in the member function)
# Test Output: done
# Test Output: adding foo and foo
# Test Output: adding foo and foo (in the member function)
# Test Output: done
# Test Output: adding other and foo
# Test Output: adding foo and other (in the member function)
# Test Output: adding foo and other
# Test Output: adding foo and other (in the member function)
# Test Output: adding foo and foo
# Test Output: adding foo and foo (in the member function)
# Test Output: done


unsafe.extern (printf)


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
    Foo() + 1
    printf("done\n")
    1 + Foo()
    printf("done\n")
    two_foo = Foo() + Foo()
    printf("done\n")
    (1 + two_foo + 1) + Foo()
    printf("done\n")
)
