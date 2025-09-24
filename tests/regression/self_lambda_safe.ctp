# Test Output: yo
# Test Output: in f:2
# Test Output: dead
# Test Output: yo
# Test Output: in f2:2
# Test Output: in lambda1:3
# Test Output: yo
# Test Output: in lambda2:4
# Test Output: in f2:3
# Test Output: dead


def (use_count, selph:
    unsafe.extern(ceto.get_underlying)
    return (&ceto.get_underlying(selph))->use_count()
)
    
 

class (Foo:
    a  # template class
    
    def (f:
        # rewritten as this->a:
        std.cout << self.a << "\n"
        
        # non-trivial use of 'self': (shared_from_this())
        std.cout << "in f:" << use_count(self) << "\n"
    )
    
    def (f2:
        # rewritten as this->a:
        std.cout << self.a << "\n"
        
        # non-trivial use of self
        std.cout << "in f2:" << use_count(self) << "\n"
        
        # more non-trivial use of self
        
        outer = lambda (:
            std.cout << "in lambda1:" << use_count(self) << "\n"
            l = lambda (:
                std.cout << self.a << "\n"
                return
            )
            l()
            std.cout << "in lambda2:" << use_count(self) << "\n"
            return
        )
        outer()
        
        std.cout << "in f2:" << use_count(self) << "\n"
    )
    
    def (destruct:
        std.cout << "dead\n"
    )
)

def (main:
    Foo("yo").f()
    Foo("yo").f2()
)
    
