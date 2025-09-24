# Test Output: 144

def (main:
    class (Foo:
        def (doit:
            unsafe.extern(printf)
            printf("%d\n", 55 + 89)
        )
    )

    Foo().doit()
)
    
