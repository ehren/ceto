include <map>

# This file excercises a few macros so that the standard library macros (.cth files in the include directory containing defmacros) are compiled (DLLs written to the ceto package dir)

#include (python_syntax_compatibility)  # this is only added automatically if using actual python syntax

def (main:
    arr = [1, 2, 3]

    # listcomp
    arr2 = [x*2, for(x in arr)]

    # boundscheck
    val = arr2[0]

    # simple map init
    #m: std.map = { 0: 1, 1: val }
    #val2 = m[0]
    #static_cast<void>(val2)  # TODO we should probably allow passing a reference to static_cast<void> - note that foo(m[0]) is fine if foo is a simple stateless func - maybe we can do better with template funcs

    #x: mut[static[int]] = 0 # python-style type declaration
    #x2: mut:static:int = 0  # default ceto syntax
    #static_assert(std.is_same_v<decltype(x), decltype(x2)>)
)
