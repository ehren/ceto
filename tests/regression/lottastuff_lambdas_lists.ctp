

def (stuff, a:
    return: a[0]
)

def (takes_func_arg_arg, func, arg1, arg2:
    return: func(arg1, arg2)
)

# unnecessarilly_higher_order_def(foo) (x:
#     pass
# )

def (foo, x:
    return x + 1
)

# def (default_args, x=[], y = 2:
#     x.append(2)
#     return x
# )

def (main:
    x : mut = []
    zz = [1,2,3]
    # yy = [zz[0], foo(zz[0])]
    xx = [[1,2],[2,3]]
    xx2 : mut = []
    xx3 : mut = []
    xxanother = xx
    # xxanother2 : auto = xxanother  # TODO this should work but the type inference naively thinks 'auto' is a valid type for a vector element. TODO this should also be 'mut' now
    xxanother2 : mut:[[int]] = xxanother
    xxanother3 : mut = xxanother
    xx2.append(xxanother2)
    xx3.append(xxanother3)
    xxanother2[0] = [7,7,7]
    xxanother3[1] = [8,7,6]
    printf("xxanother2 %d
", xxanother2[0][0])
    printf("xxanother %d
", xxanother[0][0])

    lfunc = lambda (x, y, return x + y )
    lfunc2 = lambda (x, y: 
        printf("x %d y %d
", x, y)
        return x + y 
    )

    huh = takes_func_arg_arg(lfunc2, 14, 15)

    printf("yo:
            %d %d
", xx3[0][0][0], huh) 
    z = 5
    # (w:int) = z 
    w = z# : int
    q = foo(w + 1)
    # x.append(w)
    # if (1:
    #     # x.append(foo(w+1))
    #     x.append(zz[1])
    # else:
    #     x.append(foo(w-1))
    # )
    
    # this is a good parsing test but only works with the original implementation where type 'declarations' are simply ignored outside of special contexts (like python). now using the ':' bin op outside of special forms like 'if' and assignments, etc, generates a C++ declaration
    # if ((1:int): x.append(zz[1]) : some_type_lol elif z == 4: x.append(105) else: x.append(foo(w-1)) )

    # static_cast<void> to silence unused var warning (note: no syntax to codegen a C style cast - unless bugs).
    #if (1: x.append(zz[1]) elif z == 4: if (q == 6: (static_cast<void>)(1) else: (static_cast<void>)(10)) else: x.append(foo(w-1)))
    if (1: x.append(zz[1]), elif: z == 4: if (q == 6: (static_cast<void>)(1), else: (static_cast<void>)(10)), else: x.append(foo(w-1)))

    printf("ohsnap 
%d", x[0])

    yy = [x[0], foo(x[0])]

    y = [x[0], foo(w), w+25, ]

    printf("ohsnap2 %d %d %d
", stuff(y), y[1], yy[0])

    return: 0
)

    