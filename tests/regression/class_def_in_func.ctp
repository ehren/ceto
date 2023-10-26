# Test Output: 144

def (main:
    class (Foo:
        def (doit:
            printf("%d\n", 55 + 89)
        )
    )

    Foo().doit()
)
    