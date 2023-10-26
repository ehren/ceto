
class (Foo:

    def (doit:
        printf("%d\n", 55 + 89)
        return 1
    )
)

    
def (huh, x:  #   : Foo :
    x.doit()
)

def (main:

    f = Foo()
    huh(f)
    
    o = f #: object
    huh(o)
    
    l = [ f, o ]
)
    