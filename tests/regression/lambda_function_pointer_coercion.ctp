# Test Output: 325744

# TODO these lambda return type with decltype cases are pretty dubious - they should just require parenthesese (the post parse hacks to make them work should also not be in codegen - will break macro system)


def (blah, x: int:
    return x
)

def (main:
    l0 = lambda(x:int, 0):int  # works
    l = lambda(x:int, 0):int(0)  # works (immediately invoked)
    l2 = lambda(x:int, 0):decltype(0) # now works (special case "decltype" logic in codegen lambda to avoid thinking this is an immediately invoked (with 0) lambda with return type the keyword "decltype")
    l3 = lambda(x:int, 0):decltype(1)(2)  # now works
    l4 = lambda(x:int, lambda(y, y + x))
    std.cout << l4(1)(2)
    l5 = lambda(x:int, lambda(y, y + x))(1)(1)
    std.cout << l5
    if (not defined(_MSC_VER):
        l6 = lambda(x:int, lambda(y, y + x):int)(2)(3)
    else:
        l6 = lambda(x:int, return lambda(y, y + x):int)(2)(3)  # something about the double use of 'is void?' constexpr if (for implicit return in lambda) doesn't even parse in msvc (their bug)
    ) : pre
    std.cout << l6
    if (not defined(_MSC_VER):
        l7 = lambda(x:int, lambda(y, y + x):decltype(1))(3)(4)
    else:
        l7 = lambda(x:int, return lambda(y, y + x):decltype(1))(3)(4)
    ) : pre
    std.cout << l7
    # l8 = lambda(x:int, lambda(y, y + x)):decltype(lambda(x:int, 0))(0)(0)  # still an error
    # std.cout << l8
    static_assert(std.is_same_v<decltype(&blah), decltype(+lambda(x:int, return x))>)
    static_assert(std.is_same_v<decltype(&blah), decltype(+(lambda(x:int, return x):int))>)
    static_assert(std.is_same_v<decltype(&blah), decltype(+l0)>)
    static_assert(std.is_same_v<const:int, decltype(l)>)
    static_assert(std.is_same_v<decltype(&blah), decltype(+l2)>)
    static_assert(std.is_same_v<const:int, decltype(l3)>)
    
    # r = lambda(x:int, x+1):int(0) + lambda(x: int, x+2):int(1)  # must be overparenthesized (changing precedence of ':' below '+' for this case will botch one-liner if)
    r = (lambda(x:int, x+1):int(0)) + (lambda(x: int, x+2):int(1))
    r2 = lambda(x:int, x+1)(0) + lambda(x: int, x+2)(1)
    std.cout << r << r2
)
    
    