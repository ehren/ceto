# Test Output: 341111

include <iostream>

def (main:
    l : const:auto = lambda(x, x+1)
    #l2 : auto = lambda(x, x*2) : int  # error: must specify const/mut 
    l2 : auto:const = lambda(x, x*2) : int
    l3 = lambda(x, x*3)
    lmut : mut = lambda(x, x*4)
    std.cout << l(2) << l2(2)
    std.cout << std.is_const_v<decltype(l)>
    std.cout << std.is_const_v<decltype(l2)>
    std.cout << std.is_const_v<decltype(l3)>
    std.cout << not std.is_const_v<decltype(lmut)>
)

