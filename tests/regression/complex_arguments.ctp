unsafe.extern(printf, assert, static_cast)
    
# User Naumann: https://stackoverflow.com/a/54911828/1391250

# also re namespaces and unary : op:

# A : :T.func()
# A of type :T.func()
# (A::T).func() # (A of Type :T).func()
# (A::T).(func:int)()
# namespace(A, T).template_instantiate(int, func())



# char *(*fp)( int, float *)
# def (test, fp: fp(int,float:ptr):char:pointer:
# def (test, fp: ptr(int,float:ptr):char:pointer:
# def (test, fp: ptr(int,float:ptr):char:ptr
#     pass
# )
def (moretest2, p:
    std.cout << p << "\n"
    
    l = [1, 2, 3]
    a : std.vector<int> = l
    # a = l : std.vector<int> > 1
    # std.vector<int> a  # happily printed 
    # std.vector<int> a = 1 # also
    b = [1,2,3,4]
    # (a : std.vector<int>) = b
    
    
    # (a:1) + b   # something needs fixing with untyped_infix_expr vs typed_infix_expr (or whatever they're called) in the parser (probably need more recursivity). time to go back to simpler grammar with preparse
    
    # a > b
    # a < b < c > d
)

def (moretest, p: int: const : pointer: const : pointer: const : pointer:
    std.cout << p << "\n"
)

    
# int const *    // pointer to const int
def (test, p: int: const: pointer:
    std.cout << p << "\n"
)

# int * const    // const pointer to int
def (test, p: int: pointer: const:
    std.cout << p << "\n"
)

# int const * const   // const pointer to const int
def (test2, p: int: const: pointer: const:
    std.cout << p << "\n"
)

# int * const * p3;   // pointer to const pointer to int
def (test, p: int: pointer: const: pointer:
    std.cout << p << "\n"
)
    
# const int * const * p4;       // pointer to const pointer to const int
def (test3, p: const: int: pointer: const:
    std.cout << p << "\n"
)

def (bar, x:int:const:ref:
    printf("int by const ref %d", x)
)
    
# def (foo, items:list:string:  # pretty annoying but works or did (no longer does)
# maybe that should be string:list anyway given the above
def (foo, items:[std.string]:
    std.cout << "size: " << items.size() << "\n"
    
    for (s in items:
        std.cout << s << "\n"
    )
)
    
def (main, argc: int, argv: char:pointer:pointer:
    printf("argc %d\n", argc)
    assert(std.string(argv.unsafe[0]).length() > 0)
    
    lst = [s"hello", s"world"]
    foo(lst)
    bar(static_cast<int>(lst.size()))
)
    
