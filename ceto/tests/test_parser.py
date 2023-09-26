from ceto.parser import parse, TupleLiteral, Module

from .test_compiler import raises

import sys
import pytest


def test_parse_pointer_to_member():
    # would be easy to add to grammar but can be accomplished with cpp strings or a #define in an external header
    for line in r"""
(ATestpm.*pmfn)()    # Access the member function (https://learn.microsoft.com/en-us/cpp/cpp/pointer-to-member-operators-dot-star-and-star?view=msvc-170). fails
(pTestpm->*pmfn)()   # in c++: Parentheses required since * binds less tightly than the function call.

ATestpm.*pmd = 1  # Access the member data
pTestpm->*pmd = 2""".splitlines():
        raises(lambda: parse(line))

    parse(r"""(ATestpm.(*pmfn))()  # succeeds although dubious. fails in c++""")


def test_parse_dotdotdot():
    p = parse(r"""
......  # ok this is weird (should error in c++)
foo(...)
foo(x:bar...)
foo(x:bar..., ...)

def (tprintf: template<typename:T, typename:...:Targs>,
      format: const:char:ptr,
       value: T,
       Fargs: Targs:...:
      
    tprintf(format + 1, Fargs...)
)

    """)

    raises(lambda: (parse(r"""
def (tprintf: template<typename:T, typename:...:Targs>,
      format: const:char:ptr,
       value: T,
       Fargs ... Targs:  # when ... used as a type/ident it must use ':' separation here (there is no binary ... op)
    pass
)
    """)))


def test_one_liner_if_mut_parse():
    source = r"""
if (Foo():mut:
    std.cout << "5"
)    
if ((Foo():mut):
    std.cout << "5"
)    
if (Foo():mut: std.cout << "5" )    
if ((Foo():mut): std.cout << "5" )   
    """
    print(parse(source))


def test_less_or_equals():
    source = r"""
x <= y    
x <<= y
x >= y
x >>= y
x > y >>= y
x < y >>= z
x >= y > z
x > y >= z
x < y <= z
x <= y < z
    """
    p = parse(source)
    assert str(p) == "Module((x <= y),(x <<= y),(x >= y),(x >>= y),((x > y) >>= y),((x < y) >>= z),((x >= y) > z),((x > y) >= z),((x < y) <= z),((x <= y) < z))"


def test_compound_comparison():
    source = r"""
#myFunc < (double > (42, another_param))  # fails in parser due to bad template-disambig-char (acceptable)
myFunc<anotherFunc<blah>(42)>(43)
x : foo<bar>(42) : int + "fine"
myFunc<probably_a_type<blah>>42  # ((myFunc < probably_a_type) < (blah >> 42)))
myFunc<blah>>42  # (myFunc < (blah >> 42)))
value = 1 + number_of_bits<number >> 1>::value  # value = (1 + (number_of_bits<(number >> 1)> :: value))  # https://stackoverflow.com/questions/31447039/valid-c03-template-code-wont-compile-in-c11 
value = 1 + number_of_bits<(number >> 1)>::value  #   (value = (1 + (number_of_bits<RedundantParens(RedundantParens)([(number >> 1)])> :: value)

    
    """
    p = parse(source)
    print(p)


@pytest.mark.skipif(sys.platform == "win32", reason="problems with native stack overflow failing windows ci")
def test_stress_parser2():
    # https://peps.python.org/pep-0617/
    source = r"""
1 + 2 + 4 + 5 + 6 + 7 + 8 + 9 + 10 + ((((((11 * 12 * 13 * 14 * 15 + 16 * 17 + 18 * 19 * 20))))))
2*3 + 4*5*6
12 + (2 * 3 * 4 * 5 + 6 + 7 * 8)
    """.rstrip()  #  .strip()  TODO error in parser (error in preprocessor with .lstrip() ??? strip seems fine with other examples)

    # source *= 100000//3
    # apparently python's new peg parses the above in 1-6 secs

    # one run via pytest:
    # source *= 500  # 2m 11sec
    # source *= 100 # 20s
    source *= 50 # 10s
    parse(source)

    # could be sped up (without a total parser rewrite) by parsing blocks during indent checking (plus removal of Block/Module parsing from pyparsing defined grammar) - similar to error reparse scheme


def test_declarations_typed_calls():
    a = parse(r"""
def (puts, char:ptr):int
lambda(x:int,x):int
    """)


def test_for_typed():
    a = parse(r"""
for (x : const:auto:ref in iter(iterable).moreiter()[idx].iter() and blah + 1:
    pass
) 
for (x:int in iterable:
    pass
) 
for ((x,y) : const:auto:ref in iterable:
    pass
) 
    
    """.strip())


def test_scope_resolve_call():
    a = parse(r"""
# foo()()()
# FooList().l.push_back(f)

Foo(Foo(nullptr)).f.use_count()
(Foo(Foo(nullptr)).f).use_count()


    """)
    print(a)


def test_call_scope_resolution():
    a = parse(r"""

foo::bar()
foo::foo2::bar()
(foo::foo2)::bar()
foo::foo2::foo3::bar()
foo.bar()

bar()::blah
bar()()::blah::blah2
    
    """)
    assert str(a) == "Module((foo :: bar)(),((foo :: foo2) :: bar)(),((foo :: foo2) :: bar)(),(((foo :: foo2) :: foo3) :: bar)(),foo.bar(),(bar() :: blah),(bar()() :: (blah :: blah2)))"

    # debatable if last result should really be parsed as (bar()()::blah)::blah2 but above is ok for now


def test_errors2():
    return
    parse(r"""

def (main:
    std.cout <<"hi"
    #err(
    a(
)
    """)


def test_errors():
    return

    parse(r"""
def (main:
    a
    a
    a
    a
    a
    a
    a
    a
    if (b+:
        x+1
        #a#!
    )
    #'''
    aa
)
    """)


@pytest.mark.skipif(sys.platform == "win32", reason="problems with native stack overflow failing windows ci")
def test_stress_parser():
    import sys
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(10**6)  # risks overflowing cpython stack

    limit = 46

    parse(r"""

def (list_size, lst:
    std.cout << "list size: " << lst.size() << std.endl
)

def (main:
    list_size(""" + "["*limit + "1,2,3,4" + "]"*limit + """)
)
    """)

    sys.setrecursionlimit(old)


def test_template_call():
    parse(r"""
    
array<int, 30>()
std.array<int>
array<int>
array<int>()
if (1+std.array<int, 30>()[5]:
    pass
)
    """)


def test_non_left_recursive_impl():
    parse(r"""
    
foo()     
foo()()
foo(1,2)()
foo(1,2)(1,2)
x.operator("+")(y)
x.foo(a, b)(y)
foo[a][a]
foo[a]()
foo()[0]
foo()[5]  
foo(1,2)[5]
foo[5][5][5][5][5][5]()()()[5][5]
    
    """)


def test_call_array_access():
    parse(r"""

foo()[5]  
foo(1,2)[5]
foo[5][5][5][5][5][5]
foo[5][5][5][5][5][5]()
foo[5][5][5][5][5][5]()()
foo[5][5][5][5][5][5]()()()
foo[5][5][5][5][5][5]()()()[5]
foo[5][5][5][5][5][5]()()()[5][5]
foo()[5][5]
foo()[5][5][5]
foo()()[5][5][5]
foo()()()[5][5][5]
1+foo()()()[5][5][5]
1+foo()()[5]

foo()[5][5]()
foo()[5]()

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
# test_call_array_access()
# test_non_left_recursive_impl()