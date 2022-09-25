from compiler import compile


# if ((x = 2): (y = 1) else: (y = 2))  # if ':' had higher precedence
# if (x == 2: (y = 1) else: (y = 2))   # if ':' has lower precedence than '==' but not '='  (then it's a bug to change a comparison to assign by simply deleting one '=')

# if (x == 2: y = 1, elif: x == 3: y = 2, else: y = 3)
# if (x == 2: y = 1, elif: x == 3: y = 2, else: y = 3)


def test_left_assoc_attrib_access():
    c = compile(r"""
    
class (Foo:
    a
    b
    c
) 
    
def (main:
    f = Foo(1, 2, Foo(1, Foo(1, 2, Foo(1,2,3001)), Foo(1,2,3)))
    std.cout << f.c.b.c.c
)
    """)

    assert c == "3001"


def test_class_with_attributes_of_generic_class_type():
    c = compile(r"""
class (Foo:
    a
    b
    c
) 

class (Bar:
    a
    b
    # f : Foo  # probably need to forget about this # indeed we have
    # f : Foo<decltype(a), decltype(b), decltype(b)>  # this currently compiles but is wrong (need to auto inject shared_ptr in template specialization cases at least)
)

class (Bar2:
    a
    b
    c
    f : decltype(Foo(a,b,c))  # almost as good ;)
)

class (MixedGenericConcrete:
    a
    b : int
)

# class (GenericList:
#     lst : [decltype(x)]   # this kind of thing won't work without a forward declaration somewhere

#     def (init, x...:  # need syntax for template varargs
#         self.lst = *x # need different syntax than python !! or do we
#         self.lst = x... # maybe
#     )
#     
# )
# or instead
# class (GenericList:
#     lst : []   # implicit typename T1, std::vector<T1>() 
#     dct : {}   # implicit typename T2, typename T3, std::unordered_map<T2, T3> {}
# )
# but then need explicit template instantiation to invoke...

def (main:
    f = Foo(1,2,3)
    f2 = Foo(1,2,[3])
    # f3 = Foo(1,2,[])
    # f3.c.append(1)
    f4 = Foo(1, 2, Foo(1, 2, 3))
    f5 = Foo(1, 2, Foo(1, Foo(1, 2, Foo(1,2,3001)), Foo(1,2,3)))
    std.cout << f5.c.b.c.c << "\n"
    # b = Bar(1, 2, f)
    # b2 = Bar2(1, 2, 3, Foo(2,3,4))  # should work
    m = MixedGenericConcrete("e", 2)
    std.cout << m.a << m.b << "\n"
)

class (HasGenericList:
    # a : [] #?
    # needed if want
    # h = HasGenericList()
    # h.a.append(1)
    # is it really useful? (when the `append` must occur in same scope as construction)
    
    pass # FIXME: shouldn't create attribute named pass.
)

        """)

    assert c.strip() == "3001\ne2"



def test_class_attributes():
    c = compile("""
class (Foo:
    a
    b
    c
    def (bar, x:
        std.cout << "bar: " << x << std.endl 
    )
) 

# def (foo_func, f: Foo:
#     f.bar()
# )

def (main:
    f = Foo(1,2,3)
    f2 = Foo("a", 2, nullptr)
    std.cout << f.a << f2.a
    # foo_func(f)
)

    """)

    assert c == "1a"

    needtodisablepycharmjunk = r"""

class (A:
    a
    b
    c
    d  # autosyntehsized constructor A(a,b,c,d) and (template because untyped) data members
init: a, b:  # delegating constructor
    self.init(a,b,0,0)
)  

# problems with typical derived class where we don't want autosynthesized data members

# autosynthesized data members also requires rule that 0 auto synthesized attributes requires an explicit no-arg constructor (don't want =delete littered everywhere)

class (A:
    a  # autosynthesized public "T1 a";  
    b  # "T2 b"
    c
    d  # autosynthsized constructor A(a,b,c,d) : a(a), b(b),c(c),d(d) {}
    def (init, a, b:   # delegating constructor
        self.init(a,b,0,0)
    )
)  

class (B:
    def (init:  # needs explicit no arg constructor because no autosynthesized data members
        pass
    )
public:
    x      # public data  T1 x;
    y
    z
)

class (A:
    a
)

class (ADerived(A):   # need to track the generic params of A to autogenerate : A<T1, T2, T3, T4> or not? determine based on super.init call
    def (init, a, b, c, d:    # must be explicit
        super.init(a,b,c,d)   # same
    ) # results in:
    # ADerived(T1 a, T2 b, T3 c, T4 d) : A<decltype(a), decltype(b), decltype(c), decltype(d)> (a,b,c,d) {}
    
)

class (ADerived2(A):
    def (init, a:int, b, c:float, d:
        super.init(a, b, c, d)    # ensures we inherit from A<int, T1, float, T2>  etc
    )
)



    
    """



    """
class (A:
    a
    b
    c
    d
    def (foo: x

    )
private:
    b
    c

others:
    c
    d
)

# or!

class (A:
    a    # default 'init' block
    b
    c
    d
    def (foo:
        pass
    )
init:   # another constructor
    a
    b

public:  # attributes not part of constructor
    e
    f
private:
    g
    h
)


class (A:
    # autocreates constructor:
    x
    y

    # so this would be an error:
    # def (init, x, y:
    #     #self.init(...)
    #     self._x = x
    #     self._y = y
    # )

    # this instead? don't think so
    # def (init, x, y)

    def (init, x:
        self.init(x, 0)
    )

public:
    a  # these don't autogenerate a constructor
    b
protected:
    c
    d
private:
    e
    f
)


class (AA:
    a
    b
)

# class (BB:(AA,CC):
# class (BB(AA,CC):
# class (BB(AA):
#     a
#     b
#     super.init(a,b)
# )

class (BB(AA):
    c
    d
    def (init, a, b:
        super.init(a, b)
        self.c = a
        self.d = b
    )
)


"""

    # c = compile(r"""
    r"""
class (Foo:
    _a
    _b
    c = 0
    # def (init, a(_a), b(_b):
    # def (init, a, b:
    #     pass
    # ) : (_a(a), _b(b))
    def (init, a, b:
        self._a = a
        self._b = b
    done:
        printf("i'm constructed")
    )
    
    def (init, int:y:
        # self.init(0, y)
        self = init(0, y)
    body:
        printf("done (delegated)")
    )
    
    def (init, a, b:
        self.a = a  # takes place in initializer list
        # or with a delegating constructor:
        # self = Foo(a)
        # self.Foo(a)  # better?
        # self.init(a) # best?
        bb = b    # expression isn't self.something = whatever (or a single call to a delegating constructor), everything that follows takes place in constructor body 
        self.b = bb # member initializition in constructor body not initializer list
    )
)

def (main:
    pass
)    
    """


def test_one_liners():
    c = compile(r"""
def (main:
    if ((1:int): printf("1") : some_type_lol elif 2 == 4: printf("2") else: printf("3") )
    if (1:int: printf("1") : some_type_lol elif 2 == 4: printf("2") else: printf("3") )   # warning: declaration does not declare anything:  int;
)
    """)


def test_generic_refs_etc():
    c = compile(r"""
    
# def (foo, x: auto: ref:  #  error: 'auto' not allowed in function prototype
# def (foo, x: ref:  # should work (stay in template generation mode)
def (foo, x:
    return x
)
    
def (main:
    x = 1
    xref = x : auto : ref  # actually works. could just auto inject auto in the local var case?
    y = 2 : const : auto
    z = 3 : const : auto : ref
    # w = 4 : const : ref : auto   #   const & auto w = 4;   # not valid c++ syntax
    
    r = xref : const : int : ref
    r2 = xref : int : const : ref
    # r = xref : ref
    
    # p = 0 : ptr  # generating "*p = 0;" is bad
    p = &x : const : auto : ptr
    p2 = &p : const : auto : ptr : ptr
    p3 = &x : int:const:ptr
    # p4 = &x : const:ptr:int   #  const * int p4 = (&x);  error expected unqualifief id
    
    
    # want to support
    # w1 = x : ref   # really auto:ref
    # w2 = x : const:ref # really  const:auto:ref
    # w3 = &x : ptr # really  auto:ptr
    # w4 = &x : const:ptr # really const:auto:ptr
    
    # rules:  # have to look at outer expression node...
    # see ptr - output auto*
    # see const:ptr - output const auto* 
    
    foo(1)
)
    """)


def test_py14_map_example():
    c = compile(r"""
def (map, values, fun:
    results = []
    for (v in values:
        results.append(fun(v))
    )
    return results
)

def (foo, x:int:
    std.cout << x
    return x
)

def (foo_generic, x:
    std.cout << x
    return x
)

def (main:
    l = [1, 2, 3, 4]
    map(map(l, lambda (x: #int:
        std.cout << x
        x*2
    )), lambda (x:
        std.cout << x
        x
    ))
    map(l, foo)
    # map(l, foo_generic)  # error
    map(l, lambda (x:int, foo_generic(x)))  # need type printing for lambda args (when lambda arg is typed, clang 14 -O3 produces same code as passing foo_generic<int>)
    map(l, lambda (x, foo_generic(x)))  # why does this even work? note: clang 14 -O3 produces at least an extra allocation vs passing foo_generic<int>. 
    map(l, foo_generic<int>)  # new template specialization syntax...
)
	""")

    assert c == "123424681234123412341234"


# let's fix the existing vector/decltype bugs before this madness:
# def test_c_array_types():
#     c = compile("""
#
# def (main:
#     ar = [[1,2,3,4], [2,3,4,5]] : int[2][4]
#     for (i in ar:
#         std.cout << i
#     )
# )
#     """)


def test_range_iota():
    c = compile("""

def (main:
    for (i in range(10):
        std.cout << i
    )
    for (i in range(0, 10):
        std.cout << i
    )
    for (i in range(-10, 10):
        std.cout << i
    )
)

""")

    assert c.strip() == "01234567890123456789-10-9-8-7-6-5-4-3-2-10123456789"



def _alternate_syntax():
    return
    # meh these examples make searching defs vs uses eg (foo  vs foo( more difficult
    # also
    # f = lambda (x:
    #    1
    # )
    # or one liner
    # f = lambda (x, 1)
    # should these better be thought of as application of unary op 'lambda' to a tuple
    # or as a call to a higher order function? keeping def the same as lambda is better.
    c = compile("""

# def as a unary oparator (same precedence as return ...
def bar(x:int:const:ref:
    printf("int by const ref %d", x)
)

# ugly: call to the func as the type of the def
def: foo(items:[string]:
    std.cout << "size: " << items.size() << "\n"

    # barely makes sense if syntactically valid
    for: s in items(:
        std.cout << s << "\n"
    )
    
    # for as a unary operator
    for s in items(:
        std.cout << s << "\n"
    )
    
    if (x == 1) (:   # would parse ok now but def not
        pass
    elif x == 5:
        pass
    else:
        0
    )
)

def main(argc: int, argv: char:ptr:ptr:
    printf("argc %d\n", argc)
    printf("%s\n", argv[0])

    lst = ["hello", "world"] 
    foo(lst)
    bar(lst.size())
)
    """)

# use x: int(int)  # std.Function
# x: int(int):ptr   # special case this one? require int(int):std.Function:ptr  for a raw pointer to std::Function
# hmm func returning pointer to int
# (int:ptr)(int,float)
# func ptr version
# (int:ptr)(int,float) : ptr
#need better function ptr syntax:
# ptr : int(int,float)  # fine. pointer to std.Function is still int(int,float):ptr. and having a function
# hmm maybe allow template parameters if they're named T, T1, T2, ... ?
# T1(T2, T3)   <- std.function bu

def test_complex_arguments():
    c = compile(r"""
    
# User Naumann: https://stackoverflow.com/a/54911828/1391250

# also re namespaces and unary : op:

# A : :T.func()
# A of type :T.func()
# (A::T).func() # (A of Type :T).func()
# (A::T).(func:int)()
# namespace(A, T).template_instantiate(int, func())



# char *(*fp)( int, float *)
# def (test, fp: fp(int,float:ptr):char:ptr:
# def (test, fp: ptr(int,float:ptr):char:ptr:
# def (test, fp: ptr(int,float:ptr):char:ptr
#     pass
# )
def (moretest2, p:
    std.cout << p << "\n"
    
    l = [1, 2, 3]
    a = l : std.vector<int>
    # a = l : std.vector<int> > 1
    # std.vector<int> a  # happily printed # i suppose that's ok
    # std.vector<int> a = 1  # happily printed # i suppose that's ok
    b = [1,2,3,4]
    # (a : std.vector<int>) = b
    
    
    # (a:1) + b   # something needs fixing with untyped_infix_expr vs typed_infix_expr (or whatever they're called) in the parser (probably need more recursivity). time to go back to simpler grammar with preparse
    
    # a > b
    # a < b < c > d
)

def (moretest, p: int: const : ptr: const : ptr: const : ptr:
    std.cout << p << "\n"
)

    
# int const *    // pointer to const int
def (test, p: int: const: ptr:
    std.cout << p << "\n"
)

# int * const    // const pointer to int
def (test, p: int: ptr: const:
    std.cout << p << "\n"
)

# int const * const   // const pointer to const int
def (test2, p: int: const: ptr: const:
    std.cout << p << "\n"
)

# int * const * p3;   // pointer to const pointer to int
def (test, p: int: ptr: const: ptr:
    std.cout << p << "\n"
)
    
# const int * const * p4;       // pointer to const pointer to const int
def (test3, p: const: int: ptr: const:
    std.cout << p << "\n"
)

def (bar, x:int:const:ref:
    printf("int by const ref %d", x)
)
    
# def (foo, items:list:string:  # pretty annoying but works or did (no longer does)
# maybe that should be string:list anyway given the above
def (foo, items:[string]:
    std.cout << "size: " << items.size() << "\n"
    
    for (s in items:
        std.cout << s << "\n"
    )
)
    
def (main, argc: int, argv: char:ptr:ptr:
    printf("argc %d\n", argc)
    printf("%s\n", argv[0])
    
    lst = ["hello", "world"] 
    foo(lst)
    bar(lst.size())
)
    """)

    assert c.strip() == """
argc 1
./a.out
size: 2
hello
world
int by const ref 2
    """.strip()


def test_for_scope():
    c = compile("""
def (main:
    x = 5
    
    l = [1,2,3]
    for (x in l:
        x = x + 1
    )
    
    for (x in l:
        printf("%d", x)
    )
    
    for (x in [1, 2, 3]:
        x = x + 1
        printf("%d", x)
    )
        
    printf("%d", x)
)
    """)

    assert c == "2342345"


def test_indent_checker():
    pass
    # c = compile(r"""

    # """)


def test_bad_indent():
    try:
        c = compile(r"""
        
def (func, x, y:
    pass
)
        
def (main:
    foo = 1 # -0.0
    bar = 0 # 0.0
    res = foo <=> bar
    if (res < 0:
        std.cout << "-0 is less than 0"
    elif res > 0:
        std.cout << "-0 is greater than 0"
    elif res == 0:
        std.cout << "-0 and 0 are equal"
        else:
            std.cout << "-0 and 0 are unordered"
    )
    
    func(1,
1)
    
)
    """)
    except Exception as e:
        assert "Indentation error. Expected: 8 got: 12." in str(e)

    else:
        assert 0


def test_three_way_compare():
    # https://en.cppreference.com/w/cpp/language/operator_comparison#Three-way_comparison
    c = compile(r"""
def (main:
    foo = 1 # -0.0
    bar = 0 # 0.0
    res = foo <=> bar
    if (res < 0:
        std.cout << "-0 is less than 0"
    elif res > 0:
        std.cout << "-0 is greater than 0"
    elif res == 0:
        std.cout << "-0 and 0 are equal"
    else:
        std.cout << "-0 and 0 are unordered"
    )
    # x = [1,2,3]
    # x[1:2:3]
)
    
    """)

    # note that for better or worse this is valid python indentation:
    if 1 == 5:
        pass
    else:
            pass

    # we've got the same rules now
    # (not any longer, see parser.py history, back to 4 spaces == 1 indent


def test_deref_address_of():
    c = compile(r"""
    
class (Blah:
    def (huh:
        std.cout << "huh" << "\n"
    )
)

# def (hmm, x: int:ref:const:
#     pass
# )
    
def (main:
    Blah().huh()
    b = Blah()
    b.huh()  # auto unwrap via template magic
    b->huh() # no magic (but bad style for object derived class instances!)
    printf("addr %p\n", (&b)->get()) # cheat the template magic to get the real shared_ptr (or rather a pointer to it)
    # printf("addr %p\n", (&b).get()) # woo hoo this no longer works! (we previously autoderefed _every_ pointer on every attribute access...)
    # printf("addr temp %p\n", (&Blah())->get())  #  error: taking the address of a temporary object of type 'typename enable_if<!is_array<Blah> ... - good error
    # printf("use_count %ld\n", (&b).use_count())  # no autoderef for arbitrary pointers!
    printf("use_count %ld\n", (&b)->use_count())
    b_addr = &b
    printf("addr of shared_ptr instance %p\n", b_addr)
    # printf("addr %p\n", b_addr.get()) # correct error
    printf("addr %p\n", b_addr->get())
    # printf("use_count %ld\n", b_addr.use_count()) # correct error
    printf("use_count %ld\n", b_addr->use_count())
    (*b_addr).huh() # note *b_addr is a shared_ptr<Blah> so accessing via '.' already does deref magic (it's fine)
    (*b_addr)->huh()   # no deref magic is performed here (though arguably bad style)
)
    """)

    assert c.count("huh") == 5


def test_for():
    c = compile(r"""

class (Uniq:
    def (bar:
        this.x = this.x + 1
        printf("in bar %d %p\n", this.x, this)
        return this.x
    )
): unique


class (Shared:
    def (foo:
        printf("foo\n")
        return 10
    )
)

def (main:
    x = 5
    for (x in [1, 2, 3]:
        printf("%d\n", x)
        x = x + 1
    )
    
    lst = [1,2,3]
    for (x in lst:
        printf("%d\n", x)
        x = x + 1
    )
    for (x in lst:
        printf("%d\n", x)
        x = x + 1
    )
    
    
    u = []
    s = []
    for (x in [1, 2, 3, 4, 5]:
        u.append(Uniq())
        s.append(Shared())
    )
    
    for (x in u:
        printf("%d\n", x->bar())  # should not be encouraged
        printf("%d\n", x.bar())
        # zz = x # correct error
    )
    
    n = 0
    for (x in u:
        printf("bar again: %d\n", x.bar())
        # zz = x # correct error
        x = Uniq()
        n = n + 1
        if (n % 2 == 0:
            x.bar()
        )
    )
    for (x in u:
        printf("bar again again: %d\n", x.bar())
        # zz = x # correct error
        x = Uniq()
    )
    
    # v = [] #fix decltype(i)
    v = [Shared()]
    
    for (i in s:
        i.foo()
        # n = i
        v.append(i)
    )
    
    s1 = Shared()
    
    # for (v in v:  # shadowing...
    for (v1 in v:
        v1.x = 55
        
        std.cout << "v:" << v1.foo()
        # v1 = s1
    )
)
    """)


# need to change uniq_ptr managed classes/structs to use separate class hierarchy than object (even though it doesn't inherit from shared_object (enable_shared_from_this) I'm not sure you
# ever want to be upcasting to base of both shared and uniq ptr managed hierarchies.
# probably want to make 'unique' require 'struct' instead of 'func' (note that you still want get_ptr to work (compile to nothing) with uniq instances)
def test_uniq_ptr():
    c = compile(r"""
class (Foo:
    def (bar:
        printf("bar %d\n", this.x)
        return 5
    )
): unique


def (baz, f: Foo:
    f.bar()
)

def (main:
    Foo().bar()
    
    baz(Foo())
    
    f = Foo()
    f.bar()
    
    f2 = Foo()
    f2.bar()
    
    # baz(f2)  # error
    baz(std.move(f2))
    
    # lst = [Foo(), Foo(), Foo()]  # pfft https://stackoverflow.com/questions/46737054/vectorunique-ptra-using-initialization-list
    # lst = [std.move(Foo()), std.move(Foo()), std.move(Foo())]
    lst = []
    lst.append(Foo())
    f = Foo()
    # lst.append(f)  # error
    lst.append(std.move(f))
    
    lst[0].bar()
    lst[1].bar()
)
    """)


def test_reset_ptr():
    c = compile(r"""
class (Foo:
    def (bar:
        printf("bar %d\n", this.x)
    )
    
    def (destruct:
        printf("dead\n")
    )
    
    # def (handleComp, other: Foo:
    def (operator("=="), other: Foo:
        printf("in handleComp - both foo\n")
        return this.x == other.x
    )
    #def (handleComp, other: nullptr_t:
    #    printf("in handleComp - other nullptr\n")
        # return false
    #    return other == 5
    #)
    # def (handleComp, other:
    def (operator("=="), other:
        printf("in handleComp - other not foo\n")
        # return false
        return other == 5
    )
    
    # def (operator("=="), other:
    #     printf("in oper ==\n")
    #     # return true
    #     # return handleComp(other)
    #     # return other.handleComp(this)
    #     return this.handleComp(other)
    # )
)

def (operator("=="), f: Foo, other:
    return f.operator("==")(other)
)
def (operator("=="), f: Foo, other: Foo:
    return f.operator("==")(other)
)

def (operator("=="), f: Foo, other: std.nullptr_t:   # "fix" (?) use of overloaded operator '==' is ambiguous
    return not f
    #return f.operator("==")(other)
    #return nullptr == f   # i think this is safeish
)

def (main:
    f = Foo()
    f.bar()
    if (f == 5:
        printf("overload == works\n")
    )
    b = Foo()
    if (f == b:
        printf("same\n")
    else:
        printf("not same\n")
    )
    f = None
    b = None
    printf("testing for null...\n")
    if (f == None:
        printf("we're dead\n")
        # f.bar()  # crashes as expected
    )
    
    if (not f:
        printf("we're dead\n")
        # f.bar()  # crashes as expected
    )
)
    """)


    assert c.strip() == r"""
bar 0
in handleComp - other not foo
overload == works
in handleComp - both foo
same
dead
dead
testing for null...
we're dead
we're dead    
    """.strip()

#
#     """bar 0
# in oper ==
# in handleComp - other not foo
# overload == works
# in oper ==
# in handleComp - both foo
# same
# dead 0x7ff2714017a8
# dead 0x7ff2714017e8
# testing for null...
# we're dead
# we're dead
#     """

    assert "we're dead" in c


def test_parser_left_accociativity():
    c = compile(r"""
def (main:
    std.cout << 9+3 << "\n" << 9-3-2 << "\n" << - 5 - 2 - 2 << "\n" << (( -5) - 2) - 2 << "\n" << 7-3-2 << std.endl
)
    """)

    assert """
12
4
-9
-9
2
    """.strip() in c


def test_clearing_pointers_assignment():
    c = compile("""
    
class (Foo:
    def (foo:
        printf("foo\n")
        return 5
    )
)

def (main:
    f = Foo()
    f.foo()
    f2 = f
    f2.foo()
    std.cout << (&f)->use_count() << std.endl
    std.cout << (&f2)->use_count() << std.endl
    f2 = nullptr
    f = None
    printf("f %d\n", not f)
    printf("f2 %d\n", not f2)
    std.cout << (&f)->use_count() << std.endl
    std.cout << (&f2)->use_count() << std.endl
    f.foo()  # not sure if actually UB (not technically derefing NULL)
    f2.foo()
)
    """)

    assert c.strip() == r"""
foo
foo
2
2
f 1
f2 1
0
0
foo
foo
    """.strip()


def test_stress_parser():
    # at least clang hangs on this before we do
    # limit = 50

    limit = 5
    c = compile(r"""

def (list_size, lst:
    std.cout << "list size: " << lst.size() << std.endl
)

def (main:
    list_size(""" + "["*limit + "1,2,3,4" + "]"*limit + """)
)
    """)

    assert "list size: 1" in c

def test_correct_nested_left_associative_bin_op():
    # prev implementation was just ('ignore all args except first two')
    c = compile(r"""

def (list_size, lst:
    std.cout << "list size: " << lst.size() << " uh huh" << std.endl
    printf("add: %d", 1+2+3+4)
)

def (main:
    list_size([1,2,3,4])
)
    """)

    assert "list size: 4 uh huh\nadd: 10" in c

def test_cstdlib():
    c = compile(r"""
def (main:
    fp = fopen("file.txt", "w+")
    fprintf(fp, "hello %s", "world\n")
    fclose(fp)
    fp = fopen("file.txt", "r")
    
    class (Blah:
        def (huh:
            printf("huh")
        )
    )
    
    b = Blah().huh()
    # printf("Blah addr %p", b.get()) # not going to happen
    
    cs = "file.txt".c_str()
    t = std.ifstream(c"file.txt")
    buffer = std.stringstream()
    buffer << t.rdbuf()
    s = buffer.str()
    std.cout << s << "\n"
    
)
    """)
    assert "hello world\n" in c


def test_interfaces():
    c = compile(r"""
class (Blah1:
    # ugly
    # (def:A) (foo, x:A:
    #     printf("Blah1 foo\n")
    # ):int
    
    # too busy
    # def (foo:A, x:A:
    #     printf("Blah1 foo\n")
    #     x.huh()
    # ):int
    
    def (foo, x:A:
        printf("Blah1 foo\n")
        x.huh()
    ):int:A  # TODO requires checking that A not in [const, ref, ptr]
    
    def (huh:
        printf("huh 1\n")
    ):int:A
    
    # def (huh:A:
        
)

class (Blah2:
    def (foo, x:A:
        printf("Blah2 foo\n")
        x.huh()
    ):int:A
    
    def (huh:
        printf("huh 2\n")
    ):int:A
)

def (main:
    a = Blah1()
    b = Blah2()
    l = [a, b] : A
    l[0].foo(l[1])
    l[1].foo(l[0])
)
    """)

    assert """
Blah1 foo
huh 2
Blah2 foo
huh 1
    """.strip() in c


def test_vector_explicit_type_plus_mixing_char_star_and_string():
    c = compile(r"""
class (Blah:
    def (foo:
        printf("in foo method\n")
    )
)

def (main:
    a = Blah()
    b = Blah()
    l = [a, b] : Blah
    l[1].foo()
    
    s = ['a', 'b', 'c'] : string
    printf('%s is the last element. %c is the first.\n', s[2].c_str(), s[0][0])
    # print("hello", "world")
)
    """)
    assert "in foo method" in c and "c is the last element. a is the first." in c

def test_class_def_escapes():
    assert "144" in compile(r"""
class (Foo:

    def (doit:
        printf("%d\n", 55 + 89)
        return 1
    )
)

    
def (huh, x:  #   : Foo :
    x.doit()
)

def (main:

    f = Foo()
    huh(f)
    
    o = f #: object
    huh(o)
    
    l = [ f, o ]
)
    """)


def test_class_def_in_func():
    assert "144" in compile(r"""
def (main:

    class (Foo:

        def (doit:
            printf("%d\n", 55 + 89)
        )

    )

    Foo().doit()
)
    """)


def test_add_stuff():
    output = compile(r"""

class (Foo:
    def (operator("+"), foo:Foo:
        printf("adding foo and foo (in the member function)\n")
        return this
    )
    def (operator("+"), other:
        printf("adding foo and other (in the member function)\n")
        return this
    )
)

def (operator("+"), f:Foo, x:
    printf("adding foo and other\n")
    # return f + x
    return f.operator("+")(x)
    # return 10
)
def (operator("+"), x, f:Foo:
    printf("adding other and foo\n")
    # return f + x
    return f.operator("+")(x)
    # return 10
)
def (operator("+"), x:Foo, f:Foo:
    printf("adding foo and foo\n")
    # return f + x
    return f.operator("+")(x)
    # return 10
)
def (operator("+"), x, y:
    printf("adding any and any\n")
    return std.operator("+")(x, y)
)

# def (operator("+"), x, f:Foo:
#     printf("adding other and foo\n")
#     # return f + x
#     return add(f, x)
#     # return 10
# )

def (main:
    #a = f : object
    #b = y : object
    #add (y, f)
    #add (a, b)
    # add(add (y, f),
    # add (a, b))
    
    n = 1
    k = 2
    # printf("%d\n", add(n,k))
    
    Foo() + 1
    1 + Foo()
    Foo() + Foo()
    printf("%d\n", n + k)
    
    # std.cout << add(Foo(), 2) << std.endl
    # std.cout << add(Foo(), Foo()) << std.endl
    # std.cout << add(2, Foo()) << std.endl
    
    # Foo() + Foo()
    # 1 + Foo()
)
    """)

    output = output.strip()

    assert output.endswith("3")

    import re
    addinglines = list(re.findall("adding.*", output))
    assert len(addinglines) == 6

    assert "\n".join(addinglines) == """adding foo and other
adding foo and other (in the member function)
adding other and foo
adding foo and other (in the member function)
adding foo and foo
adding foo and foo (in the member function)"""


def test_add_stuff_old():
    return
    output = compile(r"""

class (Foo: #Bar :
    # x = 1
    # y = 2

    # def (init:
    #     printf("init\n")
    # )

    # def (destruct:
    #     printf("destruct\n")
    # )

    def (foo:
        printf("in foo method %p\n", this)
        return this
    )


)

def (calls_foo, x:
    x.foo()
    return x
)

def (main:
    # printf("hi")
    # x = 1
    # printf("%d", x)
    Foo().foo()
    y = Foo()
    f = y
    f.foo()
    f.x = 55
    f.foo()
    calls_foo(y).foo().foo()
    
    # a 
    
    a = f : object
    b = y : object
    
    add (y, f)
    add (a, b)
    
    # add(add (y, f),
    # add (a, b))
    n = 1
    k = 2
    printf("%d\n", add(n,k))
)
    """)


# really attribute access test
# also something about the comments requires that comments are
# stripped by the manual preprocessing before parsing
def test_correct_shared_ptr():
    output = compile(r"""

class (Foo: #Bar :
    # x = 1
    # y = 2

    # def (init:
    #     printf("init\n")
    # )

    def (destruct:
        printf("dead %p\n", this)
    )

    def (bar:
        printf("in bar\n")
    )

    def (foo:
        printf("in foo method %p\n", this)

        bar()
        this.bar()
        printf("bar attribute access %d\n", this.x)
        printf("bar attribute access %d\n", x)
        # shared_from_base()
        return this
    )


)


def (calls_foo, x:
    x.foo()
    return x
)


def (main:
    # printf("hi")
    # x = 1
    # printf("%d", x)
    Foo().foo()
    y = Foo()
    f = y
    f.foo()
    f.x = 55
    f.foo()
    calls_foo(y).foo().foo()
)
    """)

    import re
    deadlines = list(re.findall("dead.*", output))
    assert len(deadlines) == 2

    attrib_accesses = list(re.findall("bar attribute access.*", output))
    assert attrib_accesses == ["bar attribute access 0"]*4 + ["bar attribute access 55"]*8


def test_lottastuff_lambdas_lists():
    output = compile("""

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
    x = []
    zz = [1,2,3]
    # yy = [zz[0], foo(zz[0])]
    xx = [[1,2],[2,3]]
    xxx = []
    xxanother = xx
    xxanother2 = xxanother
    xxx.append(xxanother2)
    xxanother2[0] = [7,7,7]
    printf("xxanother2 %d\n", xxanother2[0][0])
    printf("xxanother %d\n", xxanother[0][0])

    lfunc = lambda (x, y, return: x + y )
    lfunc2 = lambda (x, y: 
        printf("x %d y %d\n", x, y)
        return x + y 
    )

    huh = takes_func_arg_arg(lfunc2, 14, 15)

    printf("yo:
            %d %d\n", xxx[0][0][0], huh) 
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
    if ((1:int): x.append(zz[1]) : some_type_lol elif z == 4: x.append(105) else: x.append(foo(w-1)) )

    if (1: x.append(zz[1]) elif z == 4: if (q == 6: 1 else: 10) else: x.append(foo(w-1)))

    printf("ohsnap 
%d", x[0])

    yy = [x[0], foo(x[0])]

    y = [x[0], foo(w), w+25, ]

    printf("ohsnap2 %d %d %d\n", stuff(y), y[1], yy[0])

    return: 0
)

    """)

    assert output.strip().endswith("""
xxanother2 7
xxanother 1
x 14 y 15
yo:
            1 29
ohsnap
2ohsnap2 2 6 2
    """.strip())


def test_lambdas():
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

    # for (x not in l not in not in l:
    #     1
    # )
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

def test_ifscopes_methodcalls_classes_lottastuff():
    # pytest doesn't like this and it's not the uninitialized access:
    # return

    compile(r"""

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
        # printf("hi"); printf("bye\n")  # 'need' to add ; as first class operator
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


# https://stackoverflow.com/questions/28643534/is-there-a-way-in-python-to-execute-all-functions-in-a-file-without-explicitly-c/28644772#28644772
# (sometimes want to bypass pytest on slow computer)
def _some_magic(mod):
    import inspect
    all_functions = inspect.getmembers(mod, inspect.isfunction)
    for key, value in all_functions:
        if str(inspect.signature(value)) == "()":
            value()

if __name__ == '__main__':
    import sys
    _some_magic(sys.modules[__name__])
    # test_left_assoc_attrib_access()
    # test_add_stuff()
    # test_class_attributes()
    # test_class_with_attributes_of_generic_class_type()
    # test_generic_refs_etc()
    # test_py14_map_example()
    # test_range_iota()
    # test_complex_arguments()
    # test_for_scope()
    # test_correct_shared_ptr()
    # test_bad_indent()
    # test_for()
    # three_way_compare()
    # test_deref_address_of()
    #test_uniq_ptr()
    # test_reset_ptr()
    # test_add_stuff()
    # test_stress_parser()
    # test_correct_nested_left_associative_bin_op()
    # test_ifscopes_methodcalls_classes_lottastuff()
    # test_cstdlib()
    # test_interfaces()
    # test_class_def_in_func()
    # test_class_def_escapes()
    #test_vector_explicit_type_plus_mixing_char_star_and_string()
    # test_one_liners()
