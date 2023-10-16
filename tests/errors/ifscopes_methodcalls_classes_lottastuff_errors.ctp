

def (foo:
    # return nullptr

    if (1:
        x = [2]
    else:
        x = [1,2]
    ): noscope
    printf("%d\n", x[0])
    printf("%d\n", x.at(0))
    pass
)

def (calls_method, x:
    return x.foo()
)

def (calls_size, x:
    return x.size()
)

def (bar, x:
    # if ((foo() = 0): # insane gotcha (template instantiates to always false?)
    # if ((foo() = 1): # this is the appropriate error in c++
    # if ((x = 1):
    if ((y = 1):
        # printf("hi"); printf("bye\n")  # 'need' to add ; as first class operator
        z = x + 1   
        # y=2
        z = (x + 1)
        (z = x+1)
        z = 1
        y = x + 1
        foo()
        aa = calls_size([1,2,3])
        printf("size: %ld\n", aa)
        printf("size: %ld\n", calls_size([1,2,3]))
    ) : noscope
    # TODO even 'noscope' shouldn't hoist the y=1 defined in the test to the outer scope. This is a bad test!

    if (0:
        un = 5
        # un:int = 5   # handling of this is very bad (still get the auto inserted unititialized declaration but with a new shadowed decl too)!
        # TODO just remove python like decltype hoisting (although current implementation should not just discard lhs type when hoisting!)
    ) : noscope
    printf("uninit %d", un)

    return y
)

# https://stackoverflow.com/questions/30240131/lambda-as-default-argument-fails
# def (default_args, x=[1], y=2, z = lambda (zz, return 1):
# def (default_args, x=[], y=2:  # broken by appending to copy instead of directly (now that func params const ref by default)
def (default_args, x=[1, 2], y=2:
    # x.push_back(2)
    # x.append(2)  # error x is now const & by default
    # copy = x
    # copy.append(2)
    # copy.push_back(2)
    # printf("%d %d\n", x[0], x[1])
    printf("%d %d\n", x[0], x[1])
    copy = x
    copy.push_back(2)  # TODO append deduction / "infer type of empty list" doesn't really work. fix or remove.
    # return x
    return copy
)

class (Foo:
    def (foo:
        printf("in foo method\n")
    )
)

def (main:
    default_args()
    printf("bar:%d",bar(1))
    # calls_method(object())
    calls_method(Foo())
)
    