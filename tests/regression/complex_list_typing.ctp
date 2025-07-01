# Test Output: 000000000000000000000000000000000000000000

def (f, a : [[int]]:
    std.cout << a[0][0]
    static_assert(std.is_const_v<std.remove_reference_t<decltype(a)>>)
    static_assert(std.is_reference_v<decltype(a)>)
)

def (f2, a: [[int]] = [[0, 1]]:
    std.cout << a[0][0]
    std.cout << a.at(0).at(0)
    x = a[0]
    std.cout << x[0]
    static_assert(std.is_const_v<std.remove_reference_t<decltype(a)>>)
    static_assert(std.is_reference_v<decltype(a)>)
)
    
def (main:
    l = [[0],[1],[2]]
    l2 : [[int]] = l
    l3 : std.vector<std.vector<int>> = [[0],[1],[2]]  # NOTE not portable code
    # ^ note that the space in ">> =" will likely be required when >>= operator is added (with current parser impl)
    l4 : std.vector<std.vector<int>> = l3
    l5 : [[int]] = [[0],[1]]
    l6 = [[0],[1]] : [int]
    l7 : [[int]] = [[0],[1]] : [int]
    
    # l8 : std.vector<[int]> = l7  # non-portable but also "broken" with current codegen: 
    #  error: expected a type
    #     std::vector<std::vector<decltype(int)>{int}> l8 = l7;
    # (debatable if needs fixing but TODO other more legitimate uses of embedded [] types might be legitimate. might require changes to ':'/declared_type logic)
    
    # one way to 'fix' ie evaluate [int] in a type context without typechecking its elements (also avoids need to re-introduce unary ':' as a 'type context' operator.
    l9 : std.vector<std.remove_const_t<const:[int]>> = l7
    # ^ reasonably safe even if [int] was changed to be 'const' by default in not just function params (double adding const is a compile time error)
    
    # otoh TODO: treat anything on lhs of : (even a subexpression) as a type. Use of decltype on lhs of : should pop back to expression evaluation context.
    # Though a simple typechecker that handles 'int' correctly wouldn't be the worst thing!
    
    f2 = lambda(a: [[int]]:
        static_assert(std.is_const_v<std.remove_reference_t<decltype(a)>>)
        static_assert(std.is_reference_v<decltype(a)>)
        f(a)
    )
    
    class (C:
        a: [[int]]
    )
    
    c = C(l)
    
    class (C2:
        a: [[int]] = [[0]]
        b = [[1, 0]]
    )
    
    c2 = C2()
    
    ll = [l, l2, l3, l4, l5, l6, l7, l9, c.a, c2.a]
    ll2: [[[int]]] = ll
    ll3 = [l, l2, l3] : [[int]]
    ll4 : [[[int]]] = [l, l2, l3]
    ll5 : [[[int]]] = [l, l2, l3] : [[int]]

    for (li in [ll, ll2, ll3, ll4, ll5]:
        for (lk in li:
            f(lk)
            f2(lk)
        )
    )
)
