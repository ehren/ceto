unsafe.extern(printf)

def (foo, bar:
    return bar
)

def (blah, x:int:
    return x
)

def (main:
    l = [1,2,3]
    v = l[0]
    printf("%d\n", v)
    f = lambda (:
        0
        #printf("%d\n", main)
    )
    foo(f)()
    foo(printf)
    blah(1)
    static_cast<void>(printf)
)
    
