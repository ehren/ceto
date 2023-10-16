
# now fails codegen (no braced literals in type declarations - also shouldn't allow ':' in simple calls unless we switch to that syntax for named parameters)
# (if it passed codegen would also fail c++ compilation because no current way to print "x + x;" ending with a semicolon)
def (foo:template<typename:T>:requires:requires(T:x):{ x + x }, x: T, y: T:
    return x + y
) : T
    