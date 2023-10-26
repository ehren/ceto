
class (Foo:
    def (foo, x:
        std.cout << "hi" << x << (&self)->use_count()
    )
    def (destruct:
        std.cout << "dead"
    )
)
    
def (main:
    class (Inner:
        f: Foo
        def (foo, x:int:
            std.cout << "hi"
            f.foo(x)
        )
    )

    x = 1
    f = Foo()
    lambda (f.foo(x)) ()
    
    i = Inner(f)
    lambda (i.foo(x)) ()
)
    