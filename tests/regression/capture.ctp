
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
    l = lambda (f.foo(x))
    l()  # Test output depends on the refcount of f.
         # This is written as a non-immediately invoked lambda:
         # in the future (because l is non-escaping) this test may
         # need adjusting
    
    i = Inner(f)
    lambda (i.foo(x)) ()
)
    
