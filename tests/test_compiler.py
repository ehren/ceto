from compiler import compile


def test_funcs_lists_methodcalls_lambdas_funptrs_ifscopes_semicolon():
    compile("""
def (foo, bar:
    return bar
)

def (blah, x:int:
    return x
)

def (main:
    l = [1,2,3]

    # if (1 not in l and 0 in l or 0 not in l:
    #     1
    # )

    # x in x

    for (x not in l not in not in l:
        1
    )
    printf("%d\n", l[0])
    f = lambda (:
        printf("%d\n", main)
        0
    )
    foo(f)()
    foo(printf)
    # foo(f)
    blah(1)
    printf
)
    """)

    compile("""

def (foo:
    # return None

    if (1:
        x = [2]
    else:
        x = [1,2]
    )
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
        printf("hi"); printf("bye\n")
        x=x+1
        # y=2
        x=(x+1)
        (x=x+1)
        z = 1
        y = x + 1
        foo()
        printf("size: %ld\n", calls_size([1,2,3]))
    )

    if (0:
        un = 5
    )
    printf("uninit %d", un)

    return y
)

# https://stackoverflow.com/questions/30240131/lambda-as-default-argument-fails
# def (default_args, x=[1], y=2, z = lambda (zz, return 1):
def (default_args, x=[], y=2:
    # x.append(2)
    x.append(2)
    # x.push_back(2)
    # x.push_back(2)
    printf("%d %d\n", x[0], x[1])
    return x
)

def (main:
    default_args()
    printf("bar:%d",bar(1))
    calls_method(object())
)
    """)


def test_append_to_empty_list_type_deduction():
    return
    assert compile("""
def (map, values, fun:
    results = []
    results.append(fun())
)
    """).strip() == """

    """


def test_stuff():

    0 and compile("""
    
def (map, values, fun:
    results = [1]
    results.append(fun(v))
   # for v in values:
   #     results.append(fun(v))
   # return results
    i = 0
    x = i
    i = x
    (z = i+1)
    (x+5)
    (,)
    (1,2)
    (1,)
    (1)
    
    while (i + 5:
        results.append(fun(v))
        results.pop()
        pass
    )
    return results
)
    
    """)


# my pytest is messed up or pytest is trying to interpret the strings as python...

# https://stackoverflow.com/questions/28643534/is-there-a-way-in-python-to-execute-all-functions-in-a-file-without-explicitly-c/28644772#28644772
def some_magic(mod):
    import inspect
    all_functions = inspect.getmembers(mod, inspect.isfunction)
    for key, value in all_functions:
        if str(inspect.signature(value)) == "()":
            value()

if __name__ == '__main__':
    import sys
    some_magic(sys.modules[__name__])