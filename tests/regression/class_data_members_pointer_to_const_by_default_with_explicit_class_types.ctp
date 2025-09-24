
class (Foo:
    a : int  # it's important Foo is not a template (in order to use as an ordinary type below)
    def (mutmethod: mut:
        self.a = self.a + 1
        return self.a
    )
    def (constmethod:
        return "i'm const by default"
    )
)

class (HolderMut:
    f : Foo:mut
)

class (HolderConst:
    f : Foo  # shared_ptr<const Foo> by default
)
    
def (main:
    f = Foo(1)
    h = HolderConst(f)
    std.cout << h.f.constmethod()
    
    fm : mut = Foo(2)
    hm: mut = HolderMut(fm)  # even though fm is a mut mut:Foo we must create hm as a mut mut:HolderMut because of propagate_const
    std.cout << hm.f.constmethod()
    std.cout << hm.f.mutmethod()
    
    hc = HolderConst(fm)  # ok conversion
    std.cout << hc.f.constmethod()
)
    
