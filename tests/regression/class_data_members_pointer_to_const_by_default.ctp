
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
    f2.mutmethod()
    h2 = Holder(f2)
    #std.cout << h2.f.mutmethod()  # error (good) because of propagate_const
    f2_mut_copy: mut = h2.f
    f2_mut_copy.mutmethod()  # okish behavior - our propagate_const is copyable (better than no propagate_const at all - at least we require a mut annotation to mutate)
)
    
