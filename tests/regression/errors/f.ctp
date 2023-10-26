
class (Foo:
    def (method:
        printf("no this")    
    )
) 

def (main:
    f : mut = Foo()
    f = nullptr
    f.method()
)
        