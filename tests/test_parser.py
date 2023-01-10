from parser import parse, TupleLiteral, Module


def test_non_left_recursive_impl():
    parse(r"""
    
# foo()     
# foo()()
# foo(1,2)()
# foo(1,2)(1,2)
# x.operator("+")(y)
x.foo(a, b)(y)
    
    """)


def test_call_array_access():
    parse(r"""

# needs "call_array_access" separate definition
foo()[5]  
# foo(1,2)[5]
# foo[5][5][5][5][5][5]
# foo[5][5][5][5][5][5]()
# foo[5][5][5][5][5][5]()()
# foo[5][5][5][5][5][5]()()()
foo[5][5][5][5][5][5]()()()[5] # yes^
# foo[5][5][5][5][5][5]()()()[5][5] # no 
# foo()[5][5]  # no
# foo()[5][5][5]  # no
# foo()()[5][5][5]
# foo()()()[5][5][5]
# 1+foo()()()[5][5][5]
# 1+foo()()[5]

# TODO: doesn't parse:
# foo()[5][5]()
# foo()[5]()

# these worked before
foo[5][5]
(foo())[5]
foo[5]()
foo(1,2,3)

    """)


def test_call_arrayaccess_newline():
    parse(r"""
foo(x,
1)
a[


0:

1:



     5
  ]
""")


def test_array_dict():
    parse(r"""
    
def (foo:
    # l = [1, 2, 3]
    # l[0:1:2]
    # l[0:(1:1)]
    d = {1:2, 1:2}
    a = []
    a[1:2:3]
    pass
)
def (foo:
    # l = [1, 2, 3]
    # l[0:1:2]
    # l[0:(1:1)]
    d = {1:2, 1:2}
    a = []
    a[1:2:3]
    pass
)
    
    """)


def test_need_statement():
    try:
        parse(r"""
def (bar, x:
    
)
        """)
    except:
        pass
    else:
        assert False


def test_semicolon():
    m = parse(r"""
def (bar, x:
    printf("hi"); printf("bye\n")
    printf("hi"); printf("bye\n");
    pass;
)
    
    """)


def test_tuple():
    m = parse("""
(,)
    """)
    assert isinstance(m, Module)
    t, = m.args

    assert isinstance(t, TupleLiteral)
    assert t.args == []


def test_kitchen_sink2():
    parse(r"""

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
        # printf("hi"); printf("bye\n")
        x=x+1
        # y=2
        x=(x+1)
        (x=x+1)
        z = 1
        y = x + 1
        foo()
        aa = calls_size([1,2,3])
        printf("size: %ld\n", aa)
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
        """)


def test_kitchen_sink1():
    parse("""
def(foo, x, y=2:

    #
    # 2
    "hi"
    if (x == 5:  
        huh
        
    elif x == 6:
        huh2
    )
    
    
)

eee
# a = [1,2]
    """)

    # import sys
    # sys.exit()

    parse("""
if((x=5): print(5) elif x = 4: ohyeah else: "hmm")
""")
    parse("""
# ((((xyz = 12345678))))
# abc = 5
(x = ((5+6)*7))     # Parens(=(x,*(Parens(+(5,6)),7)))
x = ((5+6))*7    # Parens(=(x,Parens(*(Parens(+(5,6)),7))))

foo(x=5, 

(y=5))

if ((x=5):
    print(5)
elif x = 4:
    ohyeah
elif x = 5:
    10
    10
else:
    10
    10
)


""")

# test_array_dict()