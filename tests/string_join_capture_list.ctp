
    
cpp'
#include <numeric>  
'
    
# https://stackoverflow.com/a/54888823/1391250
def (join, v, to_string, sep="":
    return std.accumulate(v.begin() + 1, v.end(), to_string(v[0]),
        lambda[&to_string = to_string, &sep](a, el, a + sep + to_string(el)))
)

def (main:
    l = lambda(a, std.to_string(a))
    csv = join([1, 2, 3, 4, 5], lambda[ref](a, l(a)), ", ")  # capture the outer lambda by ref just to test all by ref (&) capture list
    b = "blah"
    csv2 = join([0], lambda[val](a, b + std.to_string(a)))
    std.cout << csv << csv2
)
    
    