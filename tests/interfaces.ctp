
class (Blah1:
    # ugly
    # (def:A) (foo, x:A:
    #     printf("Blah1 foo\n")
    # ):int
    
    # This may be a bit busy but allows an unambiguous return type
    # def (foo:A, x:A:
    #     printf("Blah1 foo\n")
    #     x.huh()
    # ):int  # or ':A' if it returns an 'A'!
    
    # or explicit interface(A) although meaning of 'A' is clear from scope if already defined (not so much for auto-definition; could also add 'concept' although not sure worth it just to improve C++ compiler error messages)
    
    # We've switched to this which makes "which code uses the interfaces feature" possible via text search
    def (foo:interface(A), x:A:
        printf("Blah1 foo\n")
        return x.huh()
    ):int
    
    # Previous implementation. Totally inconcistent - how to return a shared_ptr<A> ? (that is an A in whatever-lang-called code). You can't! (or rather must hope auto return type deduction suffices!)
    # def (foo, x:A:
    #     printf("Blah1 foo\n")
    #     x.huh()
    # ):int:A  # requires checking that A not in [const, ref, ptr] - not the only problem with this approach ^^ !
    
    def (huh:interface(A):
        printf("huh 1\n")
        return 76
    ):int
    
    # def (huh:A:
        
)

class (Blah2:
    def (foo:interface(A), x:A:
        printf("Blah2 foo\n")
        return x.huh()
    ):int
    
    def (huh:interface(A):
        printf("huh 2\n")
        return 89
    ):int
)

def (main:
    a = Blah1()
    b = Blah2()
    l = [a, b] : A
    l[0].foo(l[1])
    l[1].foo(l[0])
)
    