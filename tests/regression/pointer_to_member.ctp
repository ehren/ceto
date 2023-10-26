# Test Output: func1func15522

cpp'
#define MFPTR_DOT(a, b) (a.*b)
#define MFPTR_ARROW(a, b) (a->*b)
'
    
# https://learn.microsoft.com/en-us/cpp/cpp/pointer-to-member-operators-dot-star-and-star?view=msvc-170
class (Testpm:
    num : int
    def (func1:
        std.cout << "func1"    
    )
)

pmfn = &Testpm.func1
pmd = &Testpm.num

def (main:
    a_Testpm = *Testpm(5)
    p_Testpm = &a_Testpm
    
    a_Testpm_mut : mut = *Testpm(5)
    p_Testpm_mut : mut = &a_Testpm_mut
    
    # (a_Testpm.*pmfn)()    # fails to parse
    # (pTestpm->*pmfn)()   # in c++: Parentheses required since * binds less tightly than the function call. (fails to parse)

    # a_Testpm.*pmd = 1  # fails to parse
    # p_Testpm->*pmd = 2 # fails to parse
    
    # (a_Testpm.(*pmfn))()  # parsing succeeds but fails in c++ (note autoderef here too)
    # : error: invalid use of unary ‘*’ on pointer to member
    #          ceto::mado(a_Testpm)->(*pmfn)();
    
    # (p_Testpm->(*pmfn))()  # likewise fails in c++
    # error: invalid use of unary ‘*’ on pointer to member
    #    43 |         p_Testpm -> (*pmfn)();
    
    MFPTR_DOT(a_Testpm, pmfn)()
    MFPTR_ARROW(p_Testpm, pmfn)()
    
    # MFPTR_DOT(a_Testpm, pmd) = 1  # error assignment to read only location
    MFPTR_DOT(a_Testpm_mut, pmd) = 1
    MFPTR_ARROW(p_Testpm_mut, pmd) = 2
    
    std.cout << MFPTR_DOT(a_Testpm, pmd) << MFPTR_ARROW(p_Testpm, pmd)
    std.cout << MFPTR_DOT(a_Testpm_mut, pmd) << MFPTR_ARROW(p_Testpm_mut, pmd)
)
    