

class (Foo:
    a  # template class
    
    def (f:
        # rewritten as this->a:
        std.cout << self.a << "\n"
        
        # non-trivial use of 'self': (shared_from_this())
        std.cout << "in f:" << (&self)->use_count() << "\n"
    )
    
    def (f2:
        # rewritten as this->a:
        std.cout << self.a << "\n"
        
        # non-trivial use of self
        std.cout << "in f2:" << (&self)->use_count() << "\n"
        
        # more non-trivial use of self
        
        outer = lambda (:
            std.cout << "in lambda1:" << (&self)->use_count() << "\n"
            l = lambda (:
                std.cout << self.a << "\n"
                return
            )
            l()
            std.cout << "in lambda2:" << (&self)->use_count() << "\n"
            return
        )
        outer()
        
        std.cout << "in f2:" << (&self)->use_count() << "\n"
    )
    
    def (destruct:
        std.cout << "dead\n"
    )
)

def (main:
    Foo("yo").f()
    Foo("yo").f2()
)
    