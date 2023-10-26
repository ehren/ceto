
# include"blah.ct"
# include <blah.ct>

def (main:
    l : const:auto = lambda(x, x+1)
    l2 : auto = lambda(x, x*2) : int  # just "auto" now means "const auto"
    l3 = lambda(x, x*3)
    lmut : mut = lambda(x, x*4)       # "mut" is the real "auto"
    std.cout << l(2) << l2(2)
    std.cout << std.is_const_v<decltype(l)>
    std.cout << std.is_const_v<decltype(l2)>
    std.cout << std.is_const_v<decltype(l3)>
    std.cout << not std.is_const_v<decltype(lmut)>
)
    