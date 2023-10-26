
class (Foo:
    a
    def (mutmethod: mut:
        self.a = self.a + 1
        return self.a
    )
    def (constmethod:
        return "i'm const by default"
    )
)

class (Holder:
    f
)
    
def (main:
    f = Foo(1)
    h = Holder(f)
    std.cout << h.f.constmethod()
    
    f2 : mut = Foo(2)
    h2 = Holder(f2)
    std.cout << h2.f.mutmethod()
)
    