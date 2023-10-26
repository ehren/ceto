
cpp'
#include <array>
'

def (main:
    # this is now regarded as a template by the preprocessor but not the parser
    # (resulting in a parse error). This seems acceptable (rather than allowing dubious template like things that aren't templates)
    # TODO better error message upon encountering a parse error due to presence of template disambiguation char
    # if (1 < 2 > (0):
    #     std.cout << "yes" 
    # )

    if (1 < 2 > 0:  # parsed as a comparison 
        std.cout << "yes" 
    )
    
    l = [1, 2, 3]
    lp = &l
    if (0 < lp->size():    # parsed correctly as a comparison
        std.cout << "ok"
    )
    
    a : mut:std.array<int, 3>   # mut because a const uninitialized declaration will be a C++ error
    static_cast<void>(a)
    a2 : std.array<int, 3>:mut
    static_cast<void>(a2)

    if (((std.array)<int, 25>())[5]:
        pass 
    )
    if ((std.array<int, 26>())[5]:
        pass 
    )
    # this is now an error: 1 + std.array<int, 27>() is not something you can index (see test_non_indexable_thing)
    # if ((1+std.array<int, 27>())[5]:
    #     pass 
    # )
    if (std.array<int, 28>()[5]:
        pass
    )
    if (1+std.array<int, 29>()[5]:
        pass 
    )
    
    # TODO should support semicolons for multiple statements in one liner lambda (either needs grammar change or stop to using ';' as block separator char - with ';' as a first class operator added)
    f = lambda (lambda (:
        std.cout << "hi"
        return
    ))
    f2 = lambda (return lambda (:
        std.cout << "hi"
        return
    ))
    
    # make sure array fix doesn't break function call
    f()()
    f2()()
    
    fn = std.function(lambda("yo"))
    lf = [fn]
    std.cout << lf[0]()
)

    