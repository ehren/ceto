from ceto.compiler import runtest
from ceto.parser import parse

import sys

import pytest


def compile(s):
    return runtest(s, compile_cpp=True)


def raises(func, exc=None):
    try:
        func()
    except Exception as e:
        if isinstance(exc, str):
            assert exc in str(e)
        else:
            print(e)
    else:
        assert 0



def test_inherited_constructors():
    compile(r"""
    
class (Base:
    pass  # this has a default constructor
)

class (Derived(Base):
    pass  # this does too - (c++ implicitly calls Base default constructor)
)

def (main:
    d = Derived()
)
    """)

    preamble = r"""
# deleted default constructor, explicit 1-arg constructor
class (Base:
    a: int
)

class (Derived(Base):  # Inheriting constructors because no user defined init method present. Default constructor is deleted (implicitly by c++) because it's deleted in the base class
    pass
)
    """

    good_code = r"""
def (main:
    d = Derived(5)
    std.cout << d.a
)
    """

    bad_code = r"""
def (main:
    d = Derived()
)
        """

    preamble2 = r"""
class (DerivedDerived(Derived):
    def (init:
        super.init(6)
    )
)
    """

    good_code2 = r"""
def (main:
    d = DerivedDerived()
    std.cout << d.a
)
    """

    bad_code2 = r"""
def (main:
    d2 = DerivedDerived(7)  # if a derived class implements an init method no constructors are inherited
    std.cout << d2.a
)
    """

    assert compile(preamble + good_code) == "5"
    raises(lambda: compile(preamble + bad_code))
    assert compile(preamble + preamble2 + good_code2) == "6"
    raises(lambda: compile(preamble + preamble2 + bad_code2))


def test_struct():
    c = compile(r"""
    
struct (Foo:
    x : string
)

def (by_const_ref, f : Foo:  # pass by const ref
    static_assert(std.is_same_v<decltype(f), const:Foo:ref>)
    static_assert(std.is_reference_v<decltype(f)>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(f)>>)
    std.cout << f.x
)

def (by_val, f: Foo:mut:  # pass by value
    static_assert(std.is_same_v<decltype(f), Foo>)
    static_assert(not std.is_reference_v<decltype(f)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(f)>>)
    std.cout << f.x
)

def (by_const_val, f: Foo:const:  # pass by const value (TODO perhaps this should be pass by const ref instead - bit of a perf gotcha. same problem with string/std.string and [T])
    static_assert(std.is_same_v<decltype(f), const:Foo>)
    static_assert(not std.is_reference_v<decltype(f)>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(f)>>)
    std.cout << f.x
)

def (by_mut_ref, f: Foo:ref:mut:  # pass by non-const reference
    static_assert(std.is_same_v<decltype(f), Foo:ref>)
    static_assert(std.is_reference_v<decltype(f)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(f)>>)
    f.x += "hi"
    std.cout << f.x
)

def (by_ptr, f: Foo:ptr:  # TODO - our add const for function params with raw pointers should behave like the shared_ptr case. That is, this should really be a const Foo *const - we're generating a const Foo*  (not that it's recommended to use raw pointers anywhere)
    # static_assert(std.is_same_v<decltype(f), const:Foo:ptr:const>)  # TODO this should work
    static_assert(std.is_same_v<decltype(f), const:Foo:ptr>)  # TODO this is wrong
    static_assert(not std.is_reference_v<decltype(f)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(f)>>)  # TODO this is wrong
    static_assert(std.is_const_v<std.remove_reference_t<decltype(*f)>>)  # this is right at least
    std.cout << f->x
)

def (by_ptr_all_const, f: const:Foo:ptr:const:  # TODO this is what we want for Foo:ptr 
    # static_assert(std.is_same_v<decltype(f), const:Foo:ptr:const>)
    static_assert(not std.is_reference_v<decltype(f)>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(f)>>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(*f)>>)
    std.cout << f->x
)

def (by_ptr_mut, f: Foo:ptr:mut:
    static_assert(std.is_same_v<decltype(f), Foo:ptr>)
    static_assert(not std.is_reference_v<decltype(f)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(f)>>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(*f)>>)
    f->x += "viaptr"
    std.cout << f->x
)

def (main:
    f = Foo("blah")
    by_const_ref(f)
    by_val(f)
    by_const_val(f)
    fm : mut = f  # copy
    # by_mut_ref(f)  # error: binding reference of type ‘Foo&’ to ‘const Foo’ discards qualifiers
    by_mut_ref(fm)
    by_ptr(&f)
    by_ptr_all_const(&f)
    by_ptr_mut(&fm)
    
    # by_const_ref(Foo("blah") : mut)  # TODO this should be an error not a silent 'mut' strip
                                       # Foo("blah") : mut:shared or Foo("blah") : shared:mut should be allowed
)
    """)

    assert c == "blahblahblahblahhiblahblahblahhiviaptr"



def test_pointer_to_member():
    c = compile(r"""
cpp'
#define MFPTR_DOT(a, b) (a.*b)
#define MFPTR_ARROW(a, b) (a->*b)
'
    
# https://learn.microsoft.com/en-us/cpp/cpp/pointer-to-member-operators-dot-star-and-star?view=msvc-170
class (Testpm:
    num : int
    def (func1:
        std.cout << "func1"    
    )
)

pmfn = &Testpm.func1
pmd = &Testpm.num

def (main:
    a_Testpm = *Testpm(5)
    p_Testpm = &a_Testpm
    
    a_Testpm_mut : mut = *Testpm(5)
    p_Testpm_mut : mut = &a_Testpm_mut
    
    # (a_Testpm.*pmfn)()    # fails to parse
    # (pTestpm->*pmfn)()   # in c++: Parentheses required since * binds less tightly than the function call. (fails to parse)

    # a_Testpm.*pmd = 1  # fails to parse
    # p_Testpm->*pmd = 2 # fails to parse
    
    # (a_Testpm.(*pmfn))()  # parsing succeeds but fails in c++ (note autoderef here too)
    # : error: invalid use of unary ‘*’ on pointer to member
    #          ceto::mado(a_Testpm)->(*pmfn)();
    
    # (p_Testpm->(*pmfn))()  # likewise fails in c++
    # error: invalid use of unary ‘*’ on pointer to member
    #    43 |         p_Testpm -> (*pmfn)();
    
    MFPTR_DOT(a_Testpm, pmfn)()
    MFPTR_ARROW(p_Testpm, pmfn)()
    
    # MFPTR_DOT(a_Testpm, pmd) = 1  # error assignment to read only location
    MFPTR_DOT(a_Testpm_mut, pmd) = 1
    MFPTR_ARROW(p_Testpm_mut, pmd) = 2
    
    std.cout << MFPTR_DOT(a_Testpm, pmd) << MFPTR_ARROW(p_Testpm, pmd)
    std.cout << MFPTR_DOT(a_Testpm_mut, pmd) << MFPTR_ARROW(p_Testpm_mut, pmd)
)
    """)

    assert c == "func1func15522"


def test_floating_point():
    c = compile(r"""
    
def (main:
    x = 10.0
    y = 10.00lf  # TODO ignored by codegen
    z = 100ULL   # same
)
    
    """)


def test_mut_typed_list():
    c = compile(r"""
    
def (byref, v : [int]:  # pass by const ref
    static_assert(std.is_reference_v<decltype(v)>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(v)>>)
    static_assert(std.is_same_v<decltype(v), const:std.vector<int>:ref>)
)

def (byconstval, v : const:[int]:  # pass by const val (TODO maybe a bit of a performance gotcha - should be an error or maybe still const ref)
    static_assert(not std.is_reference_v<decltype(v)>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(v)>>)
    static_assert(std.is_same_v<decltype(v), const:std.vector<int>>)
)

def (byref2, v : const:[int]:ref:  # pass by const ref
    static_assert(std.is_reference_v<decltype(v)>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(v)>>)
    static_assert(std.is_same_v<decltype(v), const:std.vector<int>:ref>)
)

def (byval, v : mut:[int]:  # pass by val
    static_assert(not std.is_reference_v<decltype(v)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(v)>>)
    static_assert(std.is_same_v<decltype(v), std.vector<int>>)
    # v.append(5)  # TODO
    v.push_back(5)
    return v
)

def (byval4, v : [int]:mut:  # pass by val
    static_assert(not std.is_reference_v<decltype(v)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(v)>>)
    static_assert(std.is_same_v<decltype(v), std.vector<int>>)
    # v.append(5)  # TODO
    v.push_back(5)
    return v
)

def (by_mut_ref, v : mut:[int]:ref:  # pass by non-const ref
    static_assert(std.is_reference_v<decltype(v)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(v)>>)
    static_assert(std.is_same_v<decltype(v), std.vector<int>:ref>)
    # v.append(5)  # TODO
    v.push_back(5)
    return v
)

def (by_mut_ref2, v : [int]:ref:mut:  # pass by non-const ref
    static_assert(std.is_reference_v<decltype(v)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(v)>>)
    static_assert(std.is_same_v<decltype(v), std.vector<int>:ref>)
    # v.append(5)  # TODO
    v.push_back(5)
    return v
)

# TODO
# def (byval2, v : mut:[int] = [1,2]:
#     static_assert(not std.is_reference_v<decltype(v)>)
#     static_assert(not std.is_const_v<std.remove_reference_t<decltype(v)>>)
#     static_assert(std.is_same_v<decltype(v), std.vector<int>>)
#     # v.append(5)  # TODO
#     v.push_back(5)
#     return v
# )

# def (byval3, v : mut = 5:
#     pass
# )

def (main:
    v : mut : [int] = [1, 2, 3]
    v.append(4)
    for (v in v:  # shadowing test
        std.cout << v
    )
    byref(v)
    by_mut_ref(v)
    by_mut_ref2(v)
    for (v in byval(v):
        std.cout << v
    )
    # for (v in byval2():
    #     std.cout << v
    # )
)
    """)

    assert c == "12341234555"


def test_autoderef_optional():
    c = compile(r"""
    
def (main:
    x : std.optional<std.string> = "blah"
    xm : mut:std.optional<std.string> = "blah"
    static_assert(std.is_same_v<decltype(x), const:std.optional<std.string>>)
    static_assert(std.is_same_v<decltype(xm), std.optional<std.string>>)
    std.cout << x.size() << x.value().size() << x.value() << x.c_str() << x.value().c_str()
    std.cout << xm.size() << xm.value().size() << xm.value() << xm.c_str() << xm.value().c_str()
    
    xm = std.nullopt
    std.cout << xm.value_or("or")
)
    
    """)

    assert c == "44blahblahblah44blahblahblahor"


def test_string_escapes():
    c = compile(r"""

def (main:
    std.cout << "\""
    std.cout << '"'
)
    """)

    assert c == '""'


def test_more_mut_const_declarations_with_class_asserts():
    c = compile(r"""
    
class (Foo:
    pass
)
# f1 : mut:Foo = Foo()

def (main:
    f = Foo()
    static_assert(std.is_same_v<decltype(f), const:std.shared_ptr<const:Foo.class>>)

    f1 : mut:Foo = Foo()
    static_assert(std.is_same_v<decltype(f1), std.shared_ptr<Foo.class>>)

    f2 : mut = Foo()
    static_assert(std.is_same_v<decltype(f2), std.shared_ptr<Foo.class>>)

    f3 : mut = Foo() : const
    static_assert(std.is_same_v<decltype(f3), std.shared_ptr<const:Foo.class>>)

    f4 = Foo() : mut
    static_assert(std.is_same_v<decltype(f4), const:std.shared_ptr<Foo.class>>)

    f5 : const = Foo() : const
    static_assert(std.is_same_v<decltype(f5), const:std.shared_ptr<const:Foo.class>>)

    f6 : const = Foo()
    static_assert(std.is_same_v<decltype(f6), const:std.shared_ptr<const:Foo.class>>)

    f7 : const = Foo() : mut
    static_assert(std.is_same_v<decltype(f7), const:std.shared_ptr<Foo.class>>)

    f8 : const:Foo = Foo() : mut  # conversion
    static_assert(std.is_same_v<decltype(f8), const:std.shared_ptr<const:Foo.class>>)

    f9 : const:Foo = Foo()
    static_assert(std.is_same_v<decltype(f9), const:std.shared_ptr<const:Foo.class>>)

    f10 : const:Foo = Foo() : const
    static_assert(std.is_same_v<decltype(f10), const:std.shared_ptr<const:Foo.class>>)
    
    f11 : Foo:weak = f
    static_assert(std.is_same_v<decltype(f11), const:std.weak_ptr<const:Foo.class>>)
    
    f12 : mut:Foo:weak = f1
    static_assert(std.is_same_v<decltype(f12), std.weak_ptr<Foo.class>>)
    
    f13 : mut:weak:Foo = f1
    static_assert(std.is_same_v<decltype(f13), std.weak_ptr<Foo.class>>)
    
    f14 : const:weak:Foo = f1
    static_assert(std.is_same_v<decltype(f14), const:std.weak_ptr<const:Foo.class>>)
)
    """)

    raises(lambda: (compile(r"""
class (Foo:
    pass
)
def (main:
    f_bad_1 : Foo:mut:const = Foo():mut
)
    """)), exc="too many mut/const specified for class type")

    raises(lambda: (compile(r"""
class (Foo:
    pass
)
def (main:
    f_bad_2 : Foo:const:mut = Foo()
)
    """)), exc="too many mut/const specified for class type")

    raises(lambda: (compile(r"""
class (Foo:
    pass
)
def (main:
    f_bad_3 : const:Foo:mut = Foo()
)
    """)), exc="too many mut/const specified for class type")

    raises(lambda: (compile(r"""
class (Foo:
    pass
)
def (main:
    f_bad_4 : mut:Foo:const = Foo()
)
    """)), exc="too many mut/const specified for class type")


def test_one_liner_if_mut():
    # TODO 'mut' is silently ignored here: c++ is "if (Foo()) {"
    0 and compile(r"""
if (Foo():mut:
    std.cout << "5"
)    
if ((Foo():mut):
    std.cout << "5"
)    
    """)

    c = compile(r"""
class (Foo:
    pass
)
    
def (main:
    # both fine:
    if (Foo():mut:
        std.cout << 5
    )    
    if ((Foo():mut):
        std.cout << 5
    )
    
    # TODO mut/const calls aren't handled in the post parse one liner if expander (allowing shared/unique/etc in more places e.g. FooStruct:shared as an easier way to write shared_ptr<const FooStruct> will cause similar problems)
    # if (Foo():mut: std.cout << 5)  # ceto.codegen.CodeGenError: ('unexpected type', (std.cout << 5)) # if statement from one_liner_expander has a Block with 1 statement 'mut:std.cout << 5'
    if ((Foo():mut): std.cout << 5)  # acceptable workaround for now
)
    """)

    assert c == "555"


def test_string_join_capture_list():
    c = compile(r"""
    
cpp'
#include <numeric>  
'
    
# https://stackoverflow.com/a/54888823/1391250
def (join, v, to_string, sep="":
    return std.accumulate(v.begin() + 1, v.end(), to_string(v[0]),
        lambda[&to_string = to_string, &sep](a, el, a + sep + to_string(el)))
)

def (main:
    l = lambda(a, std.to_string(a))
    csv = join([1, 2, 3, 4, 5], lambda[ref](a, l(a)), ", ")  # capture the outer lambda by ref just to test all by ref (&) capture list
    b = "blah"
    csv2 = join([0], lambda[val](a, b + std.to_string(a)))
    std.cout << csv << csv2
)
    
    """)

    assert c == "1, 2, 3, 4, 5blah0"


def test_attempt_use_after_free2():

    # no plans to address - be careful with multithreaded code!
    c = compile(r"""
cpp'
#include <chrono>
'

class (Foo:
    x : int = 1

    def (long_running_method: mut:
        while (x <= 5:
            std.cout << "in Foo: " << self.x << "\n"
            std.this_thread.sleep_for(std.chrono.seconds(1))
            self.x += 1
        )
    )

    def (destruct:
        std.cout << "Foo destruct\n"
    )
)

class (Holder:
    f : Foo:mut = None
    
    def (getter:
        return f
    )
)

def (main:
    g = Holder() : mut
    g.f = Foo() : mut
    
    t: mut = std.thread(lambda(:
        # g.getter().long_running_method()  # this "works" (getter returns by value ie +1 refcount) although still a race condition plus UB due to no atomics
        g.f.long_running_method()  # this is a definite use after free
    ))
    
    std.this_thread.sleep_for(std.chrono.milliseconds(2500))
    g.f = None
    
    t.join()
    
    std.cout << "ub has occured\n"
)
    """)

    assert c.strip() == r"""
in Foo: 1
in Foo: 2
in Foo: 3
Foo destruct
in Foo: 4
in Foo: 5
ub has occured
    """.strip()


def test_alias1():
    # this should be fine too
    c = compile(r"""
class (Foo:
    def (destruct:
        std.cout << "Foo destruct"
    )
)

def (aliaser, f : mut:auto:ref, g:
    std.cout << "in aliaser"
    f = nullptr
    std.cout << (&g)->use_count()  # 0
    std.cout << ((&g)->get() == nullptr)  # 1
    std.cout << (g == nullptr)  # 1
)

def (main:
    f : mut = Foo()
    aliaser(f, f)
)
    """)

    assert c == "in aliaserFoo destruct011"


def test_attempt_use_after_free():
    c = compile(r"""
class (Foo:
    def (method:
        std.cout << "method"
    )

    def (destruct:
        std.cout << "Foo destruct"
    )
)
    
class (Holder:
    f : Foo
)

def (accessor:
    g : mut:static:auto = Holder(nullptr)  # TODO we don't support the arguably more sensible 'static:mut:auto' (fine for now)
    
    return g
)

def (aliaser, f:
    g = accessor()
    g.f = nullptr
    # f.method()  # this would raise (good)
    std.cout << (f == nullptr)  # true - still safe at this point? (reference lifetime extension for the shared_ptr itself (not what it's pointing to) to then end of main?)
    std.cout << (&f)->use_count()  # 0 
    std.cout << ((&f)->get() == nullptr) # 1
)

def (main:
    f = accessor()
    f.f = Foo()  # + 1
    std.cout << (&(f.f))->use_count()
    aliaser(f.f) # + 0  (passed by const ref...)
)
    
    """)

    assert c == "1Foo destruct101"


def test_bug_constructor_param_should_be_ptr_to_mut_not_const():
    c = compile(r"""

class (Node:
    func : Node:mut
    args : [Node:mut]

    def (init,
         func,  # this was incorrectly codegening as const shared_ptr<const Node>& rather than const shared_ptr<Node>&
         args:
        self.func = func
        self.args = args
        static_assert(std.is_reference_v<decltype(func)>)
        static_assert(std.is_const_v<std.remove_reference_t<decltype(func)>>)
        static_assert(not std.is_const_v<decltype(self.func)>)
    )
)

def (main:
    std.cout << Node(nullptr, [] : Node:mut).args.size()
)
    """)

    assert c == "0"


def test_class_data_members_pointer_to_const_by_default_with_explicit_class_types():

    preamble = r"""
class (Foo:
    a : int  # it's important Foo is not a template (in order to use as an ordinary type below)
    def (mutmethod: mut:
        self.a = self.a + 1
        return self.a
    )
    def (constmethod:
        return "i'm const by default"
    )
)

class (HolderMut:
    f : Foo:mut
)

class (HolderConst:
    f : Foo  # shared_ptr<const Foo> by default
)
    """

    goodcode = r"""
def (main:
    f = Foo(1)
    h = HolderConst(f)
    std.cout << h.f.constmethod()
    
    fm : mut = Foo(2)
    hm = HolderMut(fm)
    std.cout << hm.f.mutmethod()
    
    hc = HolderConst(fm)  # ok conversion
    std.cout << hc.f.constmethod()
)
    """

    c = compile(preamble + goodcode)
    assert c == "i'm const by default3i'm const by default"

    badcode1 = r"""
def (main:
    f = Foo(1)
    h = HolderMut(f)
)
    """

    raises(lambda: compile(preamble + badcode1))

    badcode2 = r"""
def (main:
    f : mut = Foo(1)
    f.mutmethod()       # ok of course
    h = HolderConst(f)  # ok (conversion)
    h.f.mutmethod()     # not ok (f is shared_ptr<const Foo>)
)
    """

    raises(lambda: compile(preamble + badcode2))


def test_class_data_members_pointer_to_const_by_default():
    preamble = r"""
class (Foo:
    a
    def (mutmethod: mut:
        self.a = self.a + 1
        return self.a
    )
    def (constmethod:
        return "i'm const by default"
    )
)

class (Holder:
    f
)
    """

    goodcode = r"""
def (main:
    f = Foo(1)
    h = Holder(f)
    std.cout << h.f.constmethod()
    
    f2 : mut = Foo(2)
    h2 = Holder(f2)
    std.cout << h2.f.mutmethod()
)
    """

    assert compile(preamble + goodcode) == "i'm const by default3"

    badcode = r"""
def (main:
    f = Foo(1)
    h = Holder(f)
    std.cout << h.f.mutmethod()
)
    """
    raises(lambda:compile(preamble + badcode))


def test_lambda_function_pointer_coercion():
    c = compile(r"""
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
    
    """)

    assert c == "325744"


def test_ast_pure_virtual():
    c = compile(r"""

cpp'
#include <map>
'

    
class (Node:
    func : Node
    args : [Node]

    # def (repr: virtual) = 0  # error declarations must specify a return type
    def (repr: virtual) : string = 0
    
    def (name: virtual:
        return None
    ) : std.optional<string>
)

class (Identifier(Node):
    _name : string

    def (init, name:
        self._name = name
        super.init(None, [] : Node)
    )

    def (repr:
        return self._name
    ) : decltype(static_cast<Node>(None).repr())  # TODO this should be automatic if repr has 'override' specifier and no return type (though static_cast instead of static_pointer_cast is pretty sketchy)

    def (name: virtual:
        return self._name
    ) : decltype(std.declval<Node>().name())  # this is surely better (note that Node printed as shared_ptr<const(?) Node> here)
)

def (macro_trampoline, fptr : uintptr_t, matches: std.map<string, Node:mut>:
    # test case from selfhost (complicated scope and TypeOp vs .declared type lambda capture bug)
    # f2 = reinterpret_cast<decltype(+(lambda(matches:std.map<string, Node:mut>, None): Node:mut))>(fptr)  # extra parenthese due to + : precedence (this should work)
    # return (*f2)(matches)
    pass
)

def (main:
    id = Identifier("a")
    std.cout << id.name().value()
    
    f2 = reinterpret_cast<decltype(+(lambda(matches:std.map<string, Node:mut>, None): Node:mut))>(0)  
)
    
    """)

    assert c == "a"



def test_u8_string_prefix():
    # u8string not recommended (string with prefix and suffix test)
    c = compile(r"""
def (main:
    u : std.u8string = u8"1"c
    s = std.string(u.begin(), u.end())
    std.cout << s
)
    """)
    assert c == "1"


def test_plain_const():
    c = compile(r"""
g : const = 5  # codegen writes this as constexpr const g = 5 (TODO confirm this with a test)
def (main:
    c: const = 2
    static_assert(std.is_const_v<decltype(c)>)
    static_assert(std.is_const_v<decltype(g)>)
    std.cout << c << g
)
    """)
    assert c == "25"

    raises(lambda: compile(r"""
class (Foo:
    c: const = 1
)
    """), exc="const data members in C++ aren't very useful and prevent moves leading to unnecessary copying. Just use c = whatever (with no const \"type\" specified)")


def test_list_type_on_left_or_right_also_decltype_array_attribute_access():
    c = compile(r"""
class (Foo:
    a : [int]
    b : [int] = [1,2,3]
    c = [1,2,3] : int
    d = [1,2,3]
)
    
def (main:
    x:[int] = [1,2,3]
    l1 = [Foo(x)]
    lm : mut = []
    lm2 : mut = []
    lm3 : mut = []
    lm4 : mut = []
    lm5 : mut = []
    lm6 : mut = []
    lm8 : mut = []
    lm7 : mut = []
    lm9 : mut = []
    l2 = [Foo(x)] : Foo
    l3 : [Foo] = [Foo(x)]
    for (l in [l1, l2, l3]:
        lm.append(l[0].a[2])
        lm2.append(l3[0].a[2])
        a = l1[0].a[2]
        lm3.append(a)
        b = l[0].a[2]
        lm4.append(b)
        lm5.append(lm[0])
        lm6.append(lm2[0])
        lm7.append(l[0])
        lm8.append(lm7[0])
        c = l
        lm9.append(c[0])
    )
    
    std.cout << lm[0] << lm2[0] << lm4[0] << lm7[0].a[0] << lm8[0].b[1] << lm9[0].c[2]
)
    """)
    assert c == "333123"


def test_mut_classes():

    c = compile(r"""
    
class (Blah:
    x #: mut  # error unexpected placement of 'mut' (good error: const data members by default or otherwise are bad - prevents move optimizations + other wacky issues)
    def (foo:mut:
        self.x = self.x + 1
    )
)

def (main:
    b : mut = Blah(1)
    b.foo()
    std.cout << b.x
    b.x = 5
    std.cout << b.x
)

    """)

    assert c == "25"

    raises(lambda: compile(r"""
class (Blah:
    x
)

def (main:
    b = Blah(1)  # const by default
    b.x = 5      # error
)
    """))


def test_pointers_auto_const_uninitialized():
    # https://cppsenioreas.wordpress.com/2023/07/17/lconst-pconst/
    c = compile(r"""

def (main:
    val : mut:int
    val_east : int:mut
    a : int:ptr = &val  # a is const (not what it's pointing to); this is fine (roughly the behavior as if we had applied add_const_t to everything)
    a2 : int:ptr = &val_east
    *a = 5
    *a2 = 5
    # a = nullptr   # error
    # a2 = nullptr  # error
)
        """)

    raises(lambda:compile(r"""
    
def (main:
    val : mut:int
    a : int:ptr = &val  # a is const (not what it's pointing to)
    a = nullptr  # error
)
    """))


def test_pointers_auto_const():
    c = compile(r"""
def (main:
    x : const : auto = 0
    y : auto : ptr = &x
)
    
    """)



def test_references():
    raises(lambda : compile(r"""
def (main:
    x : const:auto:ref = 1
    y : mut:int:ref = x
)
    """))   # error: binding reference of type ‘int&’ to ‘const int’ discards qualifiers

    compile(r"""
def (main:
    # x : const:auto:ref = 1
    # y : int:ref = x  # no mut so const by default
    # static_assert(std::is_const_v<decltype(x)>)
    # static_assert(std::is_const_v<decltype(y)>)
    
    x:int = 0
    r2 : int : const : ref = x
    y : int:ref = x  # no mut so const by default
)
    """)

    c = compile(r"""
def (main:
    x : const:auto:ref = 1
    y : const:int:ref = x
    z : auto:ref = y
    static_assert(std.is_reference_v<decltype(x)>)
    static_assert(std.is_reference_v<decltype(y)>)
    static_assert(std.is_reference_v<decltype(z)>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(x)>>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(y)>>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(z)>>)
)
    """)

def test_better_lambda_error():
    raises(lambda: compile(r"""
def (main:
    lambda(x: x+1)
)
    """), "do you have the args wrong? [ it's lambda(x, 5) not lambda(x: 5) ] ")


def test_const_lambda_var():
    c = compile(r"""
# include"blah.ct"
# include <blah.ct>

def (main:
    l : const:auto = lambda(x, x+1)
    l2 : auto = lambda(x, x*2) : int  # just "auto" now means "const auto"
    l3 = lambda(x, x*3)
    lmut : mut = lambda(x, x*4)       # "mut" is the real "auto"
    std.cout << l(2) << l2(2)
    std.cout << std.is_const_v<decltype(l)>
    std.cout << std.is_const_v<decltype(l2)>
    std.cout << std.is_const_v<decltype(l3)>
    std.cout << not std.is_const_v<decltype(lmut)>
)
    """)
    assert c == "341111"


def test_lambda_return_type_immediately_invoked():
    c = compile(r"""
def (main:
    val = lambda(x:
        x
    ):int (5)
    std.cout << val
    val2 = lambda(x:
        # "hi".c_str()  # nice silent ub (aside: cout is not a safe interface)
        c"hi"
    ):const:char:ptr(5)
    std.cout << val2
)
    """)
    assert c == "5hi"


def test_nomore_types_on_right():
    # earlier ':' had a lower precedence (this is no longer a typed assign)
    raises(lambda: compile(r"""
def (main:
    # from an earlier test
    constval = (lambda(x:
        x
    ) : int) (6) : auto : const
)
        """), "Unexpected typed call")
    raises(lambda: compile(r"""
def (main:
    x = 0 : int
)
    """))
    raises(lambda: compile(r"""
def (main:
    (x = 0) : int
)
    """))


def test_noscope_if():
    c = compile(r"""
def (main:
    if (1:
        x = 5
    else:
        x = 4
    ) : noscope
    std.cout << x
)
    """)
    assert c == "5"
    raises(lambda: compile(r"""
def (main:
    if (1:
        x = 5
    else:
        pass
    ) : noscope
    std.cout << x
)
    """))
    raises(lambda: compile(r"""
def (main:
    if (1:
        x:int = 5
    else:
        x = 4
    ) : noscope
    std.cout << x
)
    """))
    raises(lambda: compile(r"""
def (main:
    if (1:
        x = 5
    ) : noscope
    std.cout << x
)
    """))


def test_toy_ast():
    c = compile(r"""
class (Node:
    func : Node
    args : [Node]
    
    # TODO "overridable" / "canoverride" / "yesoverride"? otherwise "final" by default
    def (repr: virtual:
        r : mut = "generic node with func " + if (self.func: self.func.repr() else: "none") + " (" + std.to_string(self.args.size()) + " args.)\n"
        for (a in self.args:
            r = r + "arg: " + a.repr()
        )
        return r
    ) : string
    
    # TODO "overridable" implies virtual destructor
) : nonfinal

class (Identifier(Node):
    name : string
    
    def (repr:
        return "identifier node with name: " + self.name + "\n"
    ) : string
    
    def (init, name:
        self.name = name
        # super.init(nullptr, std.vector<Node> {})  # this works but should't be required
        # super.init(nullptr, {})  # likewise - also not semantically identical (use of '{' and '}' nearly as dangerous as other c++ compat unsafe features)
        super.init(nullptr, [] : Node)  # nicer ceto solution
        # super.init(nullptr, [])  # transpiler error. TODO maybe just print "[]" as "{}" as a final fallback? only as a param?
    )
)

def (main:
    id = Identifier("a")
    std.cout << id.name
    id_node : Node = Identifier("a")  # TODO virtual destructor in Node if overridable or any method overridable (but only if Node is :unique ? clang warns even in shared_ptr case - false positive?)
    std.cout << static_pointer_cast<std.type_identity_t<Identifier>::element_type>(id_node).name  # TODO 'asinstance' (dynamic_pointer_cast)
    args : [Node] = [id, id_node]
    args2 = [id, id_node] : Node   # ensure specifying type of list element instead of type of list works too
    static_cast<void>(args2)  # unused
    node = Node(id, args)
    std.cout << (node.args[0] == nullptr)  # TODO do we have the precedence right here?
    std.cout << "\n" << node.repr()
    std.cout << node.args[0].repr()
)
    """)
    assert c.strip() == """
aa0
generic node with func identifier node with name: a
 (2 args.)
arg: identifier node with name: a
arg: identifier node with name: a
identifier node with name: a
    """.strip()


def test_init_generic():
    c = compile(r"""
class (Generic:
    x
    y : int
    z
    def (init, z, y:
        self.x = y
        self.y = 99
        self.z = z
    )
)

class (GenericChild(Generic):
    def (init, x:
        super.init(x, [1, 2, 3])
    )
)

def (main:
    g = Generic(101,-333)
    g2 = GenericChild(["x", "y", "z"])
    std.cout << g.x << g.y << g.z
    std.cout << g2.x[2] << g2.y << g2.z[1]
)
    """)
    assert c == "-33399101399y"


def test_super_init_fully_generic():
    c = compile(r"""
class (Generic:
    x
)

class (GenericChild(Generic):
    def (init, x:
        super.init(x)
    )
)

def (main:
    f = Generic(5)
    f2 = GenericChild("A")
    std.cout << f.x << f2.x
)
    """)
    assert c == "5A"


def test_super_init():
    c = compile(r"""
class (Generic:
    x
)

class (GenericChild(Generic):
    def (init, x: int:
        super.init(x)
    )
)

class (GenericChild2(Generic):
    y
    def (init, p:
        self.y = p
        super.init(p)
    )
)

def (main:
    f = Generic(5)
    f2 = GenericChild(5)
    f3 = GenericChild2(5)
    std.cout << f.x << f2.x << f3.x
)
    """)
    assert c == "555"


def test_dont_capture_lambda_args():
    c = compile(r"""
def (main:
    x : mut = []  # this should not be captured (that is, make sure the def of 'x' in 'x + y' points to the lambda arg 'x' and not the list 'x')
    lfunc = lambda (x, y, x + y)
    x.append(1)
    std.cout << lfunc(x[0], x[0])
)
    """)

    assert c == "2"



def test_new_find_defs_list_problem():
    # see TODO in Scope.find_defs - we should attach scopes to the nodes themselves (build scopes in earlier pass)
    c = compile("""
def (main:
    x : mut = []
    zz = [1,2,3]
    x.append(zz[1])
    std.cout << x[0]
)
    """)
    assert c == "2"


def test_constructors_with_atomic_attributes():
    c = compile(r"""
class (Foo:
    a : std.atomic<int> = 0  # this is a test of our 'diy no narrowing conversion initialization' at class scope
)

class (Foo2:
    a : const:std.atomic<int>  # const data members are problematic but we allow it if you specify the full type (though e.g. a : const = 0 is an error)
    def (init, p:int:
        self.a = p
    )
)

def (main:
    f = Foo()
    f2 = Foo2(1)
    static_assert(not std.is_const_v<decltype(f.a)>)
    static_assert(std.is_const_v<decltype(f2.a)>)
)
    """)


def test_init_with_generic_params():
    # fully generic case:
    c = compile(r"""
class (Foo:
    x
    def (init, p:
        self.x = p
    )
)

def (main:
    std.cout << Foo(5).x
)
    """)
    assert c == "5"



    # not really generic (constructor arg's type inferred from field's type)
    c = compile(r"""
class (Foo:
    x : int
    def (init, p:
        self.x = p
    )
)

def (main:
    std.cout << Foo(5).x
)
    """)
    assert c == "5"

    # c++ doesn't like this (CTAD failed - bit silly); maybe generating explicit deduction guides not the worst idea in general (we could also de-templatify this class)
    raises(lambda: compile(r"""
class (Foo:
    x
    def (init, p : int:
        self.x = p
    )
)

def (main:
    std.cout << Foo(5).x
)
    """))

    # another generic case
    c = compile(r"""
class (Foo:
    x
    y = 2
    def (init, y:
        self.x = y  # note that the name of the constructor param is immaterial
        # self.y = 2
    )
)

def (main:
    f = Foo(5)
    std.cout << f.x << f.y
)
    """)
    assert c == "52"


def test_init_with_generic_params2():

    c = compile(r"""
class (Foo:
    x : int
    y : int
    # ^ these can't be generic for now (because constructor params are typed from the decltype of default argument...)
    def (init, x = 5, y = 4:
        self.x = x
        self.y = y
    )
)

def (main:
    f1 = Foo()
    f2 = Foo(1)
    f3 = Foo(2, 3)
    
    for (f in {f1, f2, f3}:
        std.cout << f.x << f.y
    )
)
    """)
    assert c == "541423"


def test_init():
    c = compile(r"""
class (Foo:
    a : int
    def (init, x : int:
        self.a = x
    )
)

def (main:
    std.cout << Foo(5).a
)
    """)

    assert c == "5"

    raises(lambda: compile(r"""

class (Foo:
    a : int
    b : int
    def (init, x : int:
        self.a = x
    )
)
    """), "class Foo defines a constructor (init method) but does not initialize these attributes: b")

    raises(lambda: compile(r"""

class (Foo:
    a : int
    def (init, x : int:
        self.a = x
    )
)

def (main:
    Foo()  # ensure Foo lacks a default constructor
)
    """))


def test_multiple_attribute_access_method_call():
    c = compile(r"""
    
class (Foo:
    f : Foo
    def (use_count:
        return (&self)->use_count()
    )
)

class (FooList:
    l : [Foo] = []
)
    
def (main:
    f = Foo(Foo(Foo(Foo(Foo(nullptr)))))
    std.cout << f.f.f.f.f.use_count()
    
    (FooList() : mut).l.push_back(f)
    FooList().l
    # std.cout << FooList().l[0]  # exception (actually a call to .at())
    std.cout << Foo(Foo(nullptr)).f.use_count()
    std.cout << (Foo(Foo(nullptr)).f).use_count()
    FooList().l.operator("[]")(0)  # UB ! (but should compile)
    
    fl : mut = FooList()
    fl.l.push_back(f)
    std.cout << fl.l.operator("[]")(0).use_count()
)
    """)

    assert c == "2223"


def test_diy_none():
    c = compile(r"""

# all definitions at global scope constexpr by default:
None2 = nullptr
None3:auto = nullptr  # even ones with an explicit 'type'

def (main:
    std.cout << None2 << None3
    
    static_assert(std.is_const_v<decltype(None2)>)
    static_assert(std.is_const_v<decltype(None3)>)
    static_assert(std.is_same_v<decltype(None2), const:std.nullptr_t>)
)
    """)

    assert c == "nullptrnullptr"


def test_non_indexable_thing():
    compile(r"""
cpp'
#include <array>
'
    
def (main:
    1+std.array<int, 27>()[5]
)
        """)

    raises(lambda: compile(r"""
cpp'
#include <array>
'
    
def (main:
    (1+std.array<int, 27>())[5]
)
    """))


def test_attribute_call_array_access():
    c = compile(r"""
def (main:
    v = [0, 1, 2]
    # std::cout << v.data()[2]  # TODO ensure test_parser is adequate (no longer allowed in codegen)
    std::cout << v.data().unsafe_at(2)
)
    """)

    assert c == "2"


def test_bounds_check():
    raises(lambda: compile(r"""
def (main:
    v = [0, 1, 2]
    v[3]
)
    """))

    c = compile(r"""
def (main:
    v = [0, 1, 2]
    std::cout << v[2]
)
    """)
    assert c == "2"

    c = compile(r"""
def (main:
    v = [0, 1, 2]
    std::cout << v.operator("[]")(50)   # UB!
)
    """)
    int(c)

    c = compile(r"""
def (main:
    v = [0, 1, 2]
    # std::cout << (v.data())[50]  # more UB from unsafe API usage (and use of a.unsafe_at(i) aka real c++ a[i])
    # TODO ^ these are important precedence/parsing tests but we no longer allow raw array access in codegen. ensure these are tested properly in test_parser.py
    # std::cout << v.data()[50]
    std::cout << v.data().unsafe_at(50)  # UB
    
)
    """)
    int(c)


def test_scope_resolution_call_target_and_static_method():
    c = compile(r"""
    
class (Foo:
    def (blah:static:
        std.cout << "blah"
    )
)
    
def (main:
    # note different precedence of these two expressions (not sure if 'print some AttributeAccess instances with ::' needs to be more robust ie include post parse ast fixups - it will be required if we want call_or_construct wrapper for namespace resolved ceto class constructor calls e.g. f = mymodule.Foo())
    Foo::blah()
    Foo.blah()  # template metaprogramming solution to treat as scope resolution if Foo is a type, attribute access otherwise? (would be ugly if possible? would require forwarding).
    
    # note this Call node is currently not wrapped in call_or_construct (this will have to change when a module/import system is implemented):
    std.cout << std::vector(500, 5).at(499) << std::endl
    
    std::vector : using
    v = vector(500, 5)  # ensure vector survives current 'call_or_construct' handling
    std.cout << v.at(499)
)
    """)

    assert c == "blahblah5\n5"


def test_namespace():
    0 and compile(r"""

# namespace(std)  # implicit
namespace(std, views)

namespace (:
    def (foo:
        pass
    )
)

namespace (foo:
    def (foo:
        pass
    )
)

def (main:
    for (x in std.views.iota(1, 5):
        std.cout << x
    )
    foo.foo()
    foo::foo()
)
    
    """)


def test_no_narrowing_external_class():
    return
    # assuming elsewhere defined in c++:
    # struct ExternalCppClass {
    #     int x;
    #     int y;
    # };

    c = compile(r"""
def (main:
    ExternalCppClass(1,2)
    ExternalCppClass{1,2}
)
    """)

    # this is tough to disallow for c++ defined classes:
    # raises(r"""
    # arguably should be xfail but no immediate plans to address this:
    compile(r"""  
def (main:
    f: float = 0
    ExternalCppClass(1,2)
)
    """)



def test_more_dotdotdot():
    c = compile(r"""
    
# https://en.cppreference.com/w/cpp/language/parameter_pack
# template<class... Types>
# struct count
# {
#     static const std::size_t value = sizeof...(Types);
# };

# no explicit template class support yet

def (count: template<typename:...:Types>:
    return (sizeof...)(Types)   # note extra parethese to "call" non-atom
)

def (main:
    std::cout << count<int, float, char>()
)
    """)

    assert c == "3"



def test_parameter_pack():
    c = compile(r"""
    
# Example from https://en.cppreference.com/w/cpp/language/parameter_pack
# void tprintf(const char* format) // base function
# {
#     std::cout << format;
# }
#  
# template<typename T, typename... Targs>
# void tprintf(const char* format, T value, Targs... Fargs) // recursive variadic function
# {
#     for (; *format != '\0'; format++)
#     {
#         if (*format == '%')
#         {
#             std::cout << value;
#             tprintf(format + 1, Fargs...); // recursive call
#             return;
#         }
#         std::cout << *format;
#     }
# }
#  
# int main()
# {
#     tprintf("% world% %\n", "Hello", '!', 123);
# }
    
def (tprintf, format: const:char:ptr: # base function
    std.cout << format
)
    
def (tprintf: template<typename:T, typename:...:Targs>,  # recursive variadic function
      format: const:char:ptr, 
       value: T, 
       Fargs: Targs:...:
      
    while (*format != c"".unsafe_at(0):  # TODO maybe char"%" for char literal
        if (*format == c"%".unsafe_at(0):
            std.cout << value
            tprintf(format + 1, Fargs...) # recursive call
            return
        )
        std.cout << *format
        format = format + 1
    )
)
    
def (main:
    tprintf(c"% world% %\n", c"Hello", c"!".unsafe_at(0), 123);
)
    """)

    assert c == "Hello world! 123\n"


def test_forwarder():
    c = compile(r"""
    
# from https://herbsutter.com/2013/05/09/gotw-1-solution/

# template<typename T, typename ...Args>
# void forwarder( Args&&... args ) {
#     // ...
#     T local = { std::forward<Args>(args)... };
#     // ...
# }

def (forwarder: template<typename:T, typename:...:Args>,
          args: mut:Args:rref:...:  # TODO const:rref makes no sense so don't require 'mut' in this case? (not requiring 'mut' would be similar to not requiring 'mut' for a 'unique' param)
    local: T = { std.forward<Args>(args)... }
)

def (main:
    # from article:  "forwarder<vector<int>> ( 1, 2, 3, 4 ); // ok because of {}
    forwarder<std.vector<int>> (1, 2, 3, 4)
)
    """)



def test_more_conversions():
    # these are all considered non-narrowing in C++ (or at least allowed by braced initialization)
    # we want the same (without necessarilly relying on braced init)
    c = compile(r"""

def (main:
    b: bool = true
    b2 : bool = 1
    i : int = true
    # u : unsigned:int = i # error (narrowing)
    u2 : unsigned:int = 5
    ur : const:unsigned:int:ref = u2
    um = ur  # um now const by default
    static_assert(std.is_const_v<decltype(um)>)
    
    std.cout << b << b2 << i << u2 << ur << um
)
    """)

    assert c == "111555"

    raises(lambda: compile(r"""
def (main:
    u : unsigned:int = -1
)
    """))

    raises(lambda: compile(r"""
def (main:
    uc : unsigned:char = -150
)
    """))

    raises(lambda: compile(r"""
def (main:
    i = 5
    u : unsigned:int = i
)
    """))


def test_std_thread():
    c = compile(r"""

class (Bar:
    a
)
    
class (Foo:
    a : std.atomic<int> = 0
    go : std.atomic<bool> = true
    go2 : std.atomic<bool> = std.atomic<bool> {true}  # this shouldn't be / isn't necessary
)

def (main:
    f : mut = Foo()

    t : mut = std.thread(lambda(:
        while (f.a < 100000:
            std.cout << f.a << "\n"
        )
        f.go = false
    ))

    t2 : mut = std.thread(lambda(:
        while (f.go:
            f.a = f.a + 1   # took us a while to implement += etc
            f.a.operator("++")()  # alternative
            f.a.operator("++")(1) 
            f.a += 1  # += now implemented
        )
    ))

    t.join()
    t2.join()
)

    """)



def test_std_function():
    # import subprocess
    # if "clang version 11.0.0" in subprocess.getoutput("clang -v"):
    #     return

    c = compile(r"""

# another problem with half flattened TypeOp (previously, inside decltype, x:int is a TypeOf not an Identifier with .declared_type):
# (now works)
def (foo, f : decltype(std.function(lambda(x:int, 0))) = lambda(x:int, 0):
    return f(3)
)

# this required the logic in build_types that recurses over any nested TypeOp on rhs of operator ':' (newly added as of the commit that added this comment)
def (foo2, f : decltype(std.function(lambda(x:int, 0):int)) = lambda(x:int, 0):int:
    return f(3)
)

def (foo3, f : std.add_const_t<decltype(std.function(lambda(x:int, 0):int))> = lambda(x:int, 0):int:
    static_assert(std.is_const_v<decltype(f)>)
    return f(3)
)
    
def (main:
    l = lambda(x:int:
        std.cout << "hi" + std.to_string(x)
        5
    )
    
    f : std.function = l
    v = [f]
    std.cout << v[0](5) << "\n"
    std.cout << foo() << "\n"
    std.cout << foo(l) << "\n"
    std.cout << foo2() << "\n"
    std.cout << foo2(l) << "\n"
    std.cout << foo3() << "\n"
    std.cout << foo3(l)
)
    """)

    assert c == r"""hi55
0
hi35
0
hi35
0
hi35"""


def test_no_null_autoderef():
    def f():
        compile(r"""
class (Foo:
    def (method:
        printf("no this")    
    )
) 

def (main:
    f : mut = Foo()
    f = nullptr
    f.method()
)
        """)
    raises(f)

    # intentional UB to ensure the above test works:
    c = compile(r"""
class (Foo:
    def (method:
        printf("no this")    
    )
) 

def (main:
    f : mut = Foo()
    f = nullptr
    f->method()  # BAD c++ compatibility syntax. No autoderef / No autonull check.
)
    """)

    assert c == "no this"


def test_const_ptr():
    c = compile(r"""

class (Foo:
    a : int
    def (method: mut:
        pass
    )
)

def (calls_method, f:
    f.method()
)

def (main:  #
    fc : const:Foo = Foo(1)
    # fc.method()  # error method not const
    # f : const = Foo(1)  # error from c++ (const alone not valid)
    f : const:auto = Foo(1) : mut  # const shared_ptr to non-const actual Foo
    # f = nullptr  # error
    static_assert(std.is_const_v<decltype(f)>)
    f.method()
    calls_method(f)
    # calls_method(fc)  # error method not const
)
    
    """)


def test_no_complex_class_directives():
    c = compile(r"""

class (C:
    a:int
)
    
def (foo, c: C:
    pass
)

def (bar, c: const:C:
    pass
)

def (byval, c: std.type_identity_t<C>:   # not literal "C" or "const:C"/"C:const"  - ordinary function local rules apply: C simply shared_ptr<C>
    # this only holds for the circumstances in this test (byval called with a temporary should have use_count() == 1)
    assert ((&c)->use_count() > 1)
    
    # writing C:: or C. now results in just "C" not shared_ptr<C>:
    # static_assert(std.is_same_v<std.shared_ptr<C::element_type>, decltype(c)>)  # not portable ceto code of course
    # ^ so this sort of wonky stuff needs to be rewritten:
    
    # we currently print C (not in a scope resolution or attribute access context) as shared_ptr<C>
    # so this is probably the most canonical way to get at the real class (still not "portable" of course):
    static_assert(std.is_same_v<const:std.shared_ptr<std.type_identity_t<C>::element_type>, decltype(c)>)
    
    # other similar "non-portable" (imaging a non-C++ backend) code:
    # static_assert(std.is_same_v<std.shared_ptr<decltype(*c)>, decltype(c)>)  # TODO this fails because an UnOp is always overparenthesized due to current naive use of pyparsing.infix_expression (e.g. (*p).foo() is parsed correctly precedence-wise but need for parenthesese in code printing discarded or rather handled by overparenthesizing all UnOps in every context) - leading to use of overparenthesized decltype((*p)) in c++. "workaround" for now is:
    static_assert(std.is_same_v<const:std.shared_ptr<std.remove_reference_t<decltype(*c)>>, decltype(c)>)
)

def (byconstref, c: C:
    # this only holds for the circumstances in this test
    assert ((&c)->use_count() == 1)
    
    static_assert(std.is_reference_v<decltype(c)>)
)

def (main:
    c = C(1)
    foo(c)    
    bar(C(1))    # implicit conversion
    bar(c)       # implicit conversion
    
    c2 : const:C = C(2)  # implicit conversion
    c3 : const:C = c     # implicit conversion
    bar(c2)
    bar(c3)
    # foo(c2)            # error no matching function
    
    # c = c3             # error (no known conversion from shared const to non-const)
    # cmut : C = c3      # same
    
    # TODO
    # cc = C() : const  # cc is const shared_ptr<const C>
    
    c4 = C(1)
    byval(c4)
    byconstref(c4)
)
    """)


def test_if_expressions():
    c = compile(r"""

def (main:
    x = if (1:
        [1, 2]
    else:
        [2, 1]
    )
    
    std.cout << x[0] << x[1]
    
    std.cout << if (1: 2 else: 1)
)

""")

    assert c == "122"


def test_ifscopes_defnition_in_test():
    # broken by 'diy non narrowing init'
    0 and compile(r"""

def (main:
    if ((y : mut:int = 1):
        y = 5
    )
)

""")


def test_scopes_definition_in_test():
    # these only work because a simple 'y:mut = 0' does not incur a 'non-narrowing' static_assert (naive tacking on of which causes above test to fail)
    good_code = r"""
def (main:
    CONTROL_STRUCTURE ((y : mut = 0):
        y = 5
        std.cout << y
    )
)
"""

    bad_code = r"""
def (main:
    CONTROL_STRUCTURE ((y : mut = 1):
        y = 5
    )
    std.cout << y
)
"""

    bad_code2 = r"""
def (main:
    CONTROL_STRUCTURE ((y : mut = 1):
        pass
    )
    std.cout << y
)
"""

    comp = lambda code, control_structure: compile(code.replace("CONTROL_STRUCTURE", control_structure))

    for cs in ["while", "if"]:
        g = comp(good_code, cs)
        assert g == ""

        for b in [bad_code, bad_code2]:
            raises(lambda: comp(b, cs))


def test_scopes_definition_in_test_simple():
    compile(r"""
def (main:
    if ((y:mut = 1):
        y = 5
    )
)
""")

    compile(r"""
def (main:
    while ((y:mut = 1):
        y = 5
        break
    )
)
""")



def test_lambda_unevaluated_context():
    # import subprocess
    # if "clang version 11.0.0" in subprocess.getoutput("clang -v"):
    #     return

    # requires c++20
    c = compile(r"""
    
# handling of globals may change in future e.g. automatic constexpr
# test tries to ensure the below class scope lambdas not printed with a capture list
# although detecting decltype/subtype usage still necessary
g:int = 5

class (Foo:
    
    # our current 'is void lambda return?' and 'diy non-narrowing init' checks make the codegen for this typed assignment a bit large (it's fine)
    a : int = lambda(5 + g)()
    
    f : std.conditional_t<false, decltype(lambda(x, x + g)), int>
)

cg = "it's a global, no need to capture"c  # (and you can't because a const:char:ptr is not a shared_ptr<object> or is_arithmetic_v)

def (main:
    f = Foo(2)
    l = lambda (g + f.a)  # capture list for 'f' works here, g has a GlobalVariableDefinition so is not captured
    l2 = lambda (cg)  # ensure we _don't_ capture a global (this ensures this access is an ordinary c++ read of a global rather than an attempted capture that would fail the ceto::default_capture check).
    std.cout << f.f << f.a << l() << "\n" << l2()
)

    """)

    assert c == "21015\n" \
                "it's a global, no need to capture"


def test_requires_bad():
    def f():
        compile(r"""
# now fails codegen (no braced literals in type declarations - also shouldn't allow ':' in simple calls unless we switch to that syntax for named parameters)
# (if it passed codegen would also fail c++ compilation because no current way to print "x + x;" ending with a semicolon)
def (foo:template<typename:T>:requires:requires(T:x):{ x + x }, x: T, y: T:
    return x + y
) : T
    """)
    raises(f, "unexpected type")
    # raises(f, "unexpected context for typed construct")


def test_requires():
    parse(r"""
    

# this would work
requires(x:T, x + y)

# multi statement
requires(x:T, y:T:
    x + y
    x * y
)

# TODO codegen for:

def (foo: template<typename:T>:requires:requires(x : T, x + x), 
       x: T, 
       y: T:
    return x + y
) : T
    
def (foo: template<typename:T>:requires:requires(x : T:
    x + x
    x * x
), x: T, y: T:
    return x + y
) : T
    """)


def test_simple_explicit_template():
    c = compile(r"""

def (foo: template<typename:T, typename:Y>, 
       x: const:T:ref,
       y: const:Y:ref:
    return x + y
) : decltype(x*y)

def (foo: template<typename:T, typename:Y>, 
       x: T,
       y: const:Y:ref:
    return x + y
) : std.enable_if_t<std.is_pointer_v<T>, decltype(x)>
# ^ enable_if_t required here due to codegen trailing return type always style

def (main:
    std.cout << foo(1, 2)
    
    x = 5
    p = &x
    std.cout << *foo(p, 0)
)
    """)

    assert c == "35"


def test_capture():
    c = compile(r"""
class (Foo:
    def (foo, x:
        std.cout << "hi" << x << (&self)->use_count()
    )
    def (destruct:
        std.cout << "dead"
    )
)
    
def (main:
    class (Inner:
        f: Foo
        def (foo, x:int:
            std.cout << "hi"
            f.foo(x)
        )
    )

    x = 1
    f = Foo()
    lambda (f.foo(x)) ()
    
    i = Inner(f)
    lambda (i.foo(x)) ()
)
    """)
    assert c == "hi13hihi13dead"

    c = compile(r"""
def (main:
    x = 1
    y : const:int:ref = x  # fine to copy capture
    c = c"A".unsafe_at(0)  # TODO maybe c'A' for a char literal
    nullbyte: unsigned:char = 0

    lambda (:
        std.cout << x << c << y << nullbyte
        return
    ) ()
)
    """)
    assert c == "1A1\x00"

    def f2():
        compile(r"""
def (main:
    y = 5
    x : int:ptr = &y

    lambda (:
        std.cout << x
        return
    ) ()
)
        """)
    raises(f2)
    def f3():
        compile(r"""
def (main:
    s = "nope"

    lambda (:
        std.cout << s
        return
    ) ()
)
        """)
    raises(f3)
    0 and compile(r"""
def (main:
    x = 1
    class (Foo:
        a:int
        def (foo, x:int:
            std.cout << "hi" << x << (&self)->use_count()  # error: ceto::shared_from(this): invalid use of 'this' outside of a non-static member function
        )
    )
    f = Foo(1)
    lambda (f.foo(x)) ()
)
    """)


def test_braced_call():
    c = compile(r"""
    
cpp'
#include <array>
'
    
def (main:
    a = std.array<int, 3> {1,2,3}
    a3 : std.array<int, 3> = {1,2,3}
    a4 : std.array<int, 3> = std.array<int, 3> {1,2,3}
    
    v = std.vector<int> {1,2}
    v2 = std.vector<int> (30, 5)
    v3 : std.vector<int> = {30, 5}
    
    for (x in {a, a3, a4}:
        for (i in x:
            std.cout << i
        )
    )
    
    for (x in {v, v2, v3}:
        for (i in x:
            std.cout << i
        )
    )
    
    for (x in std.array { a, a3, a4 }:
        for (i in x:
            std.cout << i
        )
    )
    
    get = lambda(t, std.cout << std.get<0>(t)[0]): void
    
    t = std.tuple {a, a3, a4, v, v2, v3}
    t2 = std.make_tuple(a,v)
    
    get(t)
    get(t2)
)
    """)
    assert c == "1231231231255555555555555555555555555555530512312312311"

    def f():
        compile(r"""
cpp'
#include <array>
'
        
def (main:
    a2 = std.array<int, 3> (1,2,3)  # not supported by std::array
)
""")
    raises(f)

    def f2():
        compile(r"""
class (Foo:
    a
)

def (main:
    f = Foo{1}
)
""")
    raises(f2, "Use round parentheses for ceto-defined class/struct constructor call (curly braces are automatic)")

    def f3():
        compile(r"""
def (main:
    {
        x = 0
    }
)
        """)
    def f4():
        compile(r"""
{
    x = 0
}
        """)

    for ff in [f3, f4]:
        raises(ff, "Curly brace expression is invalid here. Use 'scope' for an anonymous scope.")

    def f5():
        compile(r"""
class (Foo:
    { x = 0 }
)
        """)
    raises(f5, "Unexpected expression in class body")


def test_implicit_conversions2():
    def f():
        c = compile(r"""
class (Point:
    a: int  # TODO get rid of automatic 'int x;'
    b: int
)

def (main:
    Point(1,2)    
    x:float = 0
    y:float = 0
    Point(x,y)    
)
    
    """)
    raises(f)


def test_c_array():
    def f():
        compile(r"""
class (Foo:
    {1,2,3}:int:a[3]
)

        """)
    # raises(f, "Unexpected typed expression")
    raises(f, "Unexpected expression in class body")

    def f2():
        compile(r"""
def (main:
    {1,2,3}:int:a[3]
)
    
    """)
    # raises(f2, "Unexpected expression in class body")
    raises(f2, "Unexpected typed expression")

    c = compile(r"""

def (main:
    pass 
    # this should work
    # a: int[3] = {1,2,3}
    
    # print as
    # int a [3] = {1,2,3};
    
    # a: int[2][2] = {{1}, {1}}
    # print as
    # int a [2][2] = ...
    
    # a: const:int[2][2] = {{1}, {1}}
    # print as
    # const int a [2][2] = ...
    
    # note c++
    # I dunno how we'd handle this: (maybe just require an indirect declaration via a separate typedef)
    # const int (&a) [2][2] = {{}};  # (rather than supporting this) const ref of an array
    # const int &a2 [2][2] = {{}};   # error: array of const references
)
    
    """)


def test_curly_brace():
    c = compile(r"""

cpp'
#include <array>
'

def (main:
    l : std.vector<std.vector<int>> = {{1}, {1,2,3}}
    l2 : std.vector<std.vector<int>> = {{1,2}}
    l3 : std.vector<std.vector<int>> = {{1}}
    l4 : std.vector<std.vector<int>> = {}


    a : std.vector<int> = {5,2}
    a2 : std.vector<std.vector<int>> = {l}  # confusing?
    a3 : std.vector<std.vector<int>> = l
    a4 : std.vector<std.vector<int>> = {{l}}

    # implement python style chained comparison?
    assert(2 == a.size() and 2 == a2.size() and 2 == a3.size() and 2 == a4.size())

    # TODO:
    # for (l in [l, l2, l3]:  # hang: "are we handling this correctly (def args)" (see self assign hang fix)
    #     for (k in l:
    #         std.cout << k
    #     )
    # )

    # this broke with previous insertion of declval:
    # for(auto && ll : std::vector<decltype(std::declval<std::vector<std::vector<int>>>())>{l, l2, l3}) {

    # now works:
    for (ll in [l, l2, l3, l4, a2]:
        for (li in ll:
            for (lk in li:
                std.cout << lk
            )
        )
    )

    std.cout << l3[0][0]

    arr: std.array<int, 4> = {{1, 2, 3, 4}}
    arr2: std.array<int, 2> = {1, 2}

    arr3: std::array<std::array<int, 3>, 2> = { { { {1, 2, 3} }, { { 4, 5, 6} } } }
    arr4: std::array<std::array<int, 3>, 2> = { { {1, 2, 3} } }
    # arr5: std::array<std::array<int, 3>, 2> = { {1, 2, 3} } # warning: suggest braces around initialization of subobject
    # arr6: std::array<std::array<int, 3>, 2> = {1, 2, 3}  # warning: suggest braces around initialization of subobject
    # arr7: std::array<std::array<int, 3>, 2> = {1}        # warning: suggest braces around initialization of subobject
    # arr8: std::array<std::array<int, 3>, 2> = 1        # error

    arr8: std::array<std::array<int, 3>, 2> = { { { {1} } } }

    std.cout << arr[3]
    std.cout << arr2[1]

    for (ll in [arr3, arr4]:
        std.cout << ll[0][0]
    )

    v = std.vector<int> (5, 42)
    std.cout << v[4]
    assert(v.size() == 5)

    # note these are parsed as 'BracedCall'
    v2 = std.vector<int> {5, 42}
    assert(v2.size() == 2)

    vv:std.vector<int> = std.vector<int> (5, 42)
    std.cout << v[4]
    assert(v.size() == 5)

    # 'BracedCall'
    vv2:std.vector<int> = std.vector<int> {5, 42}
    assert(v2.size() == 2)

    v1 : std.vector<int> = {1,2}
    vv1 : std.vector<std.vector<int>> = {v}
)
    """)

    assert c == "11231211123142114242"

    def f():
        compile(r"""
def (main:
    l : std.vector<std.vector<int>> = {1}
)
        """)
    raises(f)

    def f2():
        compile(r"""
def (main:
    l3 : std.vector<std.vector<int>> = {1,2}
)
        """)
    raises(f2)

    def f3():
        compile(r"""
def (main:
    l2 : std.vector<std.vector<int>> = 1
)
        """)
    raises(f3)

    def f4():
        compile(r"""
def (main:
    l : std.vector<int> = {1,2}
    l2 : std.vector<std.vector<int>> = l # this is arguably pretty weird too although some aggregative initialization cases are desirable
)
        """)
    raises(f4)


def test_self_lambda_safe():
    c = compile(r"""

class (Foo:
    a  # template class
    
    def (f:
        # rewritten as this->a:
        std.cout << self.a << "\n"
        
        # non-trivial use of 'self': (shared_from_this())
        std.cout << "in f:" << (&self)->use_count() << "\n"
    )
    
    def (f2:
        # rewritten as this->a:
        std.cout << self.a << "\n"
        
        # non-trivial use of self
        std.cout << "in f2:" << (&self)->use_count() << "\n"
        
        # more non-trivial use of self
        
        outer = lambda (:
            std.cout << "in lambda1:" << (&self)->use_count() << "\n"
            l = lambda (:
                std.cout << self.a << "\n"
                return
            )
            l()
            std.cout << "in lambda2:" << (&self)->use_count() << "\n"
            return
        )
        outer()
        
        std.cout << "in f2:" << (&self)->use_count() << "\n"
    )
    
    def (destruct:
        std.cout << "dead\n"
    )
)

def (main:
    Foo("yo").f()
    Foo("yo").f2()
)
    """)

    assert c == r"""yo
in f:2
dead
yo
in f2:2
in lambda1:3
yo
in lambda2:4
in f2:3
dead
"""

    c = compile(r"""
class (Foo:
    a
    def (method:
        std.cout << self.a
    )
) : unique

def (main:
    Foo(1).method()
)
    """)

    assert c == "1"

    try:
        c = compile(r"""
        
class (Foo:
    a
    def (method:
        std.cout << self.a  # this is fine
        
        lambda (:
            std.cout << self.a   # BAD! (results in the expected error)
            return
        )()
    )
) : unique

def (main:
    Foo(1).method()
)
            """)
    except Exception as e:
        print(e)
        # assert "candidate template ignored: could not match 'enable_shared_from_this' against 'Foo'" in cpp_errors
    else:
        assert 0


def test_implicit_conversions():
    try:
        c = compile(r"""
    
def (main:
    f: float = 0
    x: int = f
)
        """)
    except Exception as e:
        # type 'float' cannot be narrowed to 'int' in initializer list
        # assert 'float' in cpp_errors
        pass
    else:
        assert 0

    try:
        c = compile(r"""

def (main:
    len = -1
    x: unsigned:int = len
)
        """)
    except Exception as e:
        # assert 'explicit cast' in cpp_errors
        pass
    else:
        assert 0


def test_complicated_function_directives():
    # non trailing "return" etc

    c = compile(r"""
    
def (foo:static, x, y:
    return x + y
) : int

def (foo2: extern:"C",
        x: int,
        y: int:
    return x + y
) : int
    
def (main:
    std.cout << foo(1, 2) << foo2(3, 4)
)
    
    """)

    assert c == "37"

    # TODO T:typename = typename:blah needs work
    0 and compile(r"""
def (contains: template<typename:Container, T:typename = typename:std.decay<blah>>, c : Container:ref:ref, v: T:
    return std.find(std.begin(c), std.end(c), v) != std.end(c)
) : bool
    
    """)

    0 and compile(r"""
# //https://stackoverflow.com/a/58593692/1391250
# template <typename Container, typename T = typename std::decay<decltype(*std::begin(std::declval<Container>()))>::type>
# bool contains(Container && c, T v)
# {
#     return std::find(std::begin(c), std::end(c), v) != std::end(c);
# }

#def (contains, c : Container:ref:ref, v:
#    pass
#) : template<Container:typename, T:typename = typename:std.decay<blah>>
# the template is now printed correctly, but the above won't work with -> return type printing (probably a good thing)

# one idea to allow but no good because what about std::enable_if_t etc: (see above for better approach with type order same as var defn)
# def (template<Container:typename, T:typename = typename:std.decay<blah>>:contains, Container && c, T v:
#     return std.find(std.begin(c), std.end(c), v) != std.end(c);
# )

# allow tuple as function name (way too confusing):
# def ((template<Container:typename, T:typename = typename:std.decay<blah>>, contains), c:Container:ref:ref, v:T:
#     pass
# )

# (note that out-of-line method defs should be discouraged anyway)
# def (Foo::foo:const, x, y:
#     pass
# ):int
# vs
# def (Foo::foo:const:int, x, y:
#     pass
# ):nodiscard:const
# still not sure where/how to mark const methods (what about const block (like public) in class)

# possible optional non-trailing return type syntax (allowing explicit template definition)

# these won't allow tightening grammar to e.g. disallow "def" as an identifier (source of poor error messages with pyparsing out of the box):

# def:static:int (foo, 
#      x, y:
#     pass
# )
# 
# def:int (main:
#     pass
# )
# 
# def: template<typename:Container, T:typename = typename:std.decay<blah>>:bool (
#      contains, container:Container:ref:ref, element: T:
#     pass
# )

# this might work:
def (contains: template<typename:Container, T:typename = typename:std.decay<blah>>:std.enable_if<bleh>, 
            c: Container:ref:ref, 
            v: const:T:ref:
    return std.find(std.begin(c), std.end(c), v) != std.end(c)
) : bool

# keep in mind limited usefulness when "inline" automatically added (investigate implementation file generation)
def (foo:static, x, y:
    pass
)

(we're also locked into trailing return type always - might work but no explicit decltype(auto))


# def (Foo::foo:export:interface(A):const, x, y:  # const out of line method with other non-return type stuff (const must be last non-trailing "return type"?)
#     return x + y
# ):const:string:ref  # const return type
    """)


def test_complex_list_typing():
    import subprocess
    # if "clang version 11.0.0" in subprocess.getoutput("clang -v"):
    #     return

    c = compile(r"""
    
# TODO: anything of explicit array type in a function param list should be const& by default
def (f, a : [[int]]:
    std.cout << a[0][0]
    # FIXME:
    # static_assert(std.is_const_v<std.remove_reference_t<decltype(a)>>)
    # static_assert(std.is_reference_v<decltype(a)>)
)

# should also be const ref by default
def (f2, a: [[int]] = [[0, 1]]:
    std.cout << a[0][0]
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
    
    f2 = lambda(a : [[int]]:
        f(a)
        # FIXME:
        # static_assert(std.is_const_v<std.remove_reference_t<decltype(a)>>)
        # static_assert(std.is_reference_v<decltype(a)>)
    )
    
    class (C:
        a: [[int]]
    )
    
    c = C(l)
    
    class (C2:
        a: [[int]] = [[0]]
        # b = [[1, 0]]  # TODO simple untyped assignemt in class scope needs fix
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
    
    """)

    assert c == "0000000000000000000000000000000000000000000000000000000000"


def test_multiple_assign():
    raises(lambda: compile(r"""
def (main:
    x = y = 0  # error in c++ but eventual TODO should error early instead of generating "const auto x = const auto y = 0"
)
    """))

    c = compile(r"""
def (main:
    y : mut = 1
    x = y = 0
    std.cout << x << y
    y2 = y = x
    static_assert(std.is_same_v<decltype(y2), const:int>)
)
    """)
    assert c == "00"


def test_compound_comparison():
    c = compile(r"""
cpp'
#include <array>
'

def (main:
    # this is now regarded as a template by the preprocessor but not the parser
    # (resulting in a parse error). This seems acceptable (rather than allowing dubious template like things that aren't templates)
    # TODO better error message upon encountering a parse error due to presence of template disambiguation char
    # if (1 < 2 > (0):
    #     std.cout << "yes" 
    # )

    if (1 < 2 > 0:  # parsed as a comparison 
        std.cout << "yes" 
    )
    
    l = [1, 2, 3]
    lp = &l
    if (0 < lp->size():    # parsed correctly as a comparison
        std.cout << "ok"
    )
    
    a : mut:std.array<int, 3>   # mut because a const uninitialized declaration will be a C++ error
    static_cast<void>(a)
    a2 : std.array<int, 3>:mut
    static_cast<void>(a2)

    if (((std.array)<int, 25>())[5]:
        pass 
    )
    if ((std.array<int, 26>())[5]:
        pass 
    )
    # this is now an error: 1 + std.array<int, 27>() is not something you can index (see test_non_indexable_thing)
    # if ((1+std.array<int, 27>())[5]:
    #     pass 
    # )
    if (std.array<int, 28>()[5]:
        pass
    )
    if (1+std.array<int, 29>()[5]:
        pass 
    )
    
    # TODO should support semicolons for multiple statements in one liner lambda (either needs grammar change or stop to using ';' as block separator char - with ';' as a first class operator added)
    f = lambda (lambda (:
        std.cout << "hi"
        return
    ))
    f2 = lambda (return lambda (:
        std.cout << "hi"
        return
    ))
    
    # make sure array fix doesn't break function call
    f()()
    f2()()
    
    fn = std.function(lambda("yo"))
    lf = [fn]
    std.cout << lf[0]()
)

    """)

    assert c == "yesokhihiyo"


def test_range_signedness():
    # apparently "int unsigned" is actually valid c++
    # we do want to ensure that e.g. "unsigned:int" (resulting in codegen of "unsigned int") is never required to be written as "int: unsigned"
    c = compile(r"""
    
def (main:
    for (i in range(10):
        static_assert(std.is_same_v<decltype(i), int>)
        std.cout << i
    )
    u : unsigned:int = 10
    # for (i in range(u):  # TODO probably should fix
    z : unsigned:int = 0  # workaround
    for (i in range(z, u):
        static_assert(std.is_same_v<decltype(i), int:unsigned>)
        static_assert(std.is_same_v<decltype(i), unsigned:int>)
        std.cout << i
    )
)

    """)

    raises(lambda: compile(r"""

def (main:
    u : unsigned:int = 10
    for (i in range(u, -10):
        pass
    )
)
    """))


def test_ptr_not_simple_type_context():
    c = compile(r"""
def (main:
    x = 0
    xmut : mut = 0
    y : const:int:ptr = &x
    y2 : int:ptr:mut
    y2 = &xmut
    y3 : mut:int:ptr
    y3 = &xmut
    hmm = reinterpret_cast<int:ptr>(1)
    static_cast<void>(y)
    static_cast<void>(y2)
    static_cast<void>(y3)
    static_assert(not std.is_same_v<decltype(nullptr), int:ptr>)
    printf("%p", static_cast<void:ptr>(hmm))
)
    """)

    # assert c == "0x1"
    assert c.startswith("0") and c.endswith("1")

    try:
        compile(r"""
def (main:
    hmm = reinterpret_cast<ptr:int>(1)   # should be int:ptr
)
        """)
    except Exception as e:
        # assert "error: type name requires a specifier or qualifier" in cpp_errors
        pass
    else:
        assert 0



def test_a_andand_b_wrong():

    raises(lambda: compile(r"""
def (main:
    if (1 & (&2):  # this would be rejected by the c++ compiler
        pass
    )
    if (1 && 2:    # but this raises a syntax error in the transpiler
        pass
    )
)
    """))


def test_contains_helper():
    c = compile(r"""
# https://stackoverflow.com/questions/571394/how-to-find-out-if-an-item-is-present-in-a-stdvector
def (contains, container, element: const:typename:std.remove_reference_t<decltype(container)>::value_type:ref:
    return std.find(container.begin(), container.end(), element) != container.end()
)

def (main:
    l = [0, 1, 2, 10, 19, 20]
    for (i in range(20):
        if (contains(l, i):
            std.cout << i
        )
    )
)
    
""")

    assert c == "0121019"


def test_ensure_func_params_const_ref():
    c = compile(r"""
class (FooGeneric:
    a
)
    
class (FooConcrete:
    a : string
)

class (FooGenericUnique:
    a
) : unique

class (FooConcreteUnique:
    a : string
) : unique

def (func, f:
    static_assert(std.is_const_v<std.remove_reference_t<decltype(f)>>)
    static_assert(std.is_reference_v<decltype(f)>)
    std.cout << "generic " << f.a << std.endl
)
    
def (func, f : FooConcrete:
    static_assert(std.is_const_v<std.remove_reference_t<decltype(f)>>)
    static_assert(std.is_reference_v<decltype(f)>)
    std.cout << "FooConcrete " << f.a << std.endl
)

def (func, f : FooConcreteUnique:
    # static_assert(std.is_const_v<decltype(f)>)  # TODO this and all params should still be const (at least in const by default mode...). 
    static_assert(not std.is_reference_v<decltype(f)>)
    std.cout << "FooConcreteUnique " << f.a << std.endl
)

# now raises: CodeGenError: Invalid specifier for class type (although maybe this case should be allowed)
# def (func2, f : const: FooConcreteUnique: ref:
#     static_assert(std.is_const_v<std.remove_reference_t<decltype(f)>>)
#     static_assert(std.is_reference_v<decltype(f)>)
#     std.cout << "FooConcreteUnique " << f.a << std.endl
# )

def (byval, f : auto:
    static_assert(not std.is_reference_v<decltype(f)>)  # when this is the last use, arguably bad insertion of std::move here? maybe it's expected (comment no longer relevant: we no longer apply std::move willy nilly to the last use of all vars, just those known to be :unique local/funcparm ceto class instances)
    std.cout << "byval " << f.a << "\n"
)

def (main:
    f = FooGeneric("yo")
    f2 = FooConcrete("hi")
    func(f)
    func(f2)
    func(FooGenericUnique("hi"))
    f3 = FooConcreteUnique("hey")
    f4 : mut = FooConcreteUnique("hello")
    # func2(std.move(f4))
    # func2(FooConcreteUnique("hello"))
    # func(f3)
    std.cout << f3.a << "\n"  # make sure the above call isn't the last use of f3...
    func(f4)
    func(FooConcreteUnique("yo"))
    byval(f4)
    # byval(f3)  # error call to deleted blah blah (f3 is const)
)
    """)

    assert c == r"""generic yo
FooConcrete hi
generic hi
hey
generic hello
FooConcreteUnique yo
byval hello
"""

def test_constructors():
    0 and compile(r"""
    
class (GenericParamInConstructorOnly:
    # b   # error: not all generic params initialized in constructor?
    def (init, a:  # needs to count as generic param
        pass
    )
)


class (ConstructorInitializesDataMember:
    a               # needs to be regarded as same generic param as
    def (init, a:   # the constructor param e.g. make_shared<Blah<decltype(a_arg)>>(a_arg)
        self.a = a  # only regard as same if assign to data member
    )
)

class (Bad1:
    a
    b
    c
    def (init, a: # make_shared<Blah<decltype(a), int, int>>(a)
        self.a = a
        self.b = 0
        self.c = 0  
    )
    
    def (init, b:
        self.b = b
        self.a = 0
        self.c = 0
    )
    
    # Delegating(5) ?
    # C++ will error on ambiguous call but
    # TODO: codegen should be changed from:
    # make_shared<Blah<decltype(x), decltype(y), decltype(z)>>(x,y,z);  // necessary to track which params are generic (need to appear as decltypes in the template-id)
    # to
    # make_shared<decltype(Blah(x, y, z))>(x,y,z);
    # which should leave the matter up to C++. all dubious generic params tracking removable?
    
    # also TODO
    # new in c++20
    # auto constructor generation for structs allowing Blah(x, y, z) syntax (more strict than current examples would allow). does it add 'explicit' in the one-arg case?
    # https://stackoverflow.com/questions/69331785/new-type-of-auto-generated-constructor-in-c20
    # https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p0960r3.html
    # seems to suggest yes
    # otoh what about preferring brace initialization (in codegen) to disallow narrowing conversions?
)

class (Bad2:
    a
    b
    def (init, a:
        self.a = a
        slf.b = 0
    )

    def (init:
        self.a = 0
        # self.b = 0
        self.b = 0.5
    )
)

    """)


def test_scope_resolution():
    c = compile(r"""

def (main:
    std.cout  : using  # this should be the encouraged syntax
    std::endl : using  # but for additional C++ compat
    
    # However, regarding implicit namespaces e.g. std.cout vs std::endl
    # is there a precedence mismatch problem with the tighter binding scope resolution operator in C++? (when our parse tree is built using '.'). Can't think of problematic example 
    
    cout << "hi" << endl << std::endl << std.endl
)
    """)

    assert c == "hi\n\n\n"


def test_lambda_void_deduction_and_return_types():
    c = compile(r"""

def (is_void:
    pass
)

def (main:
    f = lambda(x:
        std.cout << x << std.endl
        void()  # still need this (cout not void but can't return it)
    )
    f(1)
    static_assert(std.is_same_v<decltype(f(1)), void>)
    static_assert(std.is_same_v<decltype(is_void()), void>)

    f2 = lambda(x:
        x
    )
    std.cout << f2(2) << std.endl
    static_assert(std.is_same_v<decltype(f2(2)), int>)
    
    f3 = lambda (x:
        std.cout << x << std.endl
    ) : void
    f3(3)
    static_assert(std.is_same_v<decltype(f3(3)), void>)
    
    f4 = lambda (x:
        std.cout << x << std.endl
        x
    ) : int
    std.cout << f4(4) << std.endl
    static_assert(std.is_same_v<decltype(f4(4)), int>)
    
    # still necessary to wrap in parens if immediately invoking?
    val = (lambda(x:
        x
    ) : int) (5)
    std.cout << val << std.endl
)
    """)

    assert c.strip() == r"""
1
2
3
4
4
5
    """.strip()


def test_typed_identifiers_as_cpp_variable_declarations():
    c = compile(r"""
def (main:
    x:int:mut
    x = 0
    (static_cast<void>)(x)  # silence unused variable warning
    
    f = lambda (y:const:char:ptr, z:int:mut:
        std: using: namespace  # variable declaration 'like'
        t : typedef : int
        w : t = 3
        cout << y << z << w << endl
        z = 2  # unrelated test that lambda params treated as defs in 'find_defs'.
        cout << z << endl
        void()
    )
    
    f("hi".c_str(), 5)
)
    """)
    assert c.strip() == "hi53\n2"


def test_manual_implementation_of_proper_refcounted_return_self():
    # Note: this is more of a template + scope resolution syntax test

    c = compile(r"""
    
class (A:
    a
)

# note that this approach needs adjustments for template classes (codegen now correctly handles 'self' even in template case via ceto::shared_from)
class (S:
    def (foo:
        # note that S:: or S. is treated as static attribute access of the c++ class S (fool transpiler by inserting std.type_identity_t so that S as an identifier's parent is not an instance of ScopeResolution/AttributeAccess):
        return std.static_pointer_cast<std.type_identity_t<S>::element_type>(shared_from_this())
    )
    
    def (foo2:
        # alternately
        return std.static_pointer_cast<std.remove_reference<decltype(*this)>::type>(shared_from_this())
        
        # no need for overparenthization any more (debatable if we need to parse this now that other template parse improvements have been made)
        return (std.static_pointer_cast<std.remove_reference<decltype(*this)>::type>)(shared_from_this())
    ) : S  # no need for return type (but S correctly handled as shared_ptr<S> here)
)

def (main:
    s = S()
    std.cout << (&s)->use_count() << std.endl
    s2 = s.foo()
    std.cout << (&s2)->use_count() << std.endl
    a = A(s)
    std.cout << (&s2)->use_count() << std.endl
    s3 = a.a.foo2()
    std.cout << (&s)->use_count() << std.endl
    std.cout << (&s3)->use_count() << std.endl
    
    # dyncast(B, a)
    # staticcast(B, a)  # not a good idea to make static_pointer_cast convenient
    # isinstance(a, B)
    # asinstance(a, B)   # std::dynamic_pointer_cast<B>(a)  # maybe this is better than 'dyncast'
)
    
    """)

    assert c == "1\n2\n3\n4\n4\n"

def _test_higher_precedence_colon():
    return  # Nope keeping colon at lowest precedence. Down with x: int = 0. up with x = 0 : int

    # when precedence change is made, undesirable change noted is parsing "yield: x = 5" as "(yield: x)=5" etc (behaviour with 'return' noted below - current code printing happens to produce the correct code but forces operation on nonsensical AST (hence abandoning)


    # another point in favor of the existing lower precedence ':' is the complication in python's parse rules for typed assigmnemts due to the conflicting lambda syntax:
    # >>> lambda: x = 1
    #   File "<stdin>", line 1
    # SyntaxError: cannot assign to lambda
    # >>> if x = 1:
    #   File "<stdin>", line 1
    #     if x = 1:
    #          ^
    # SyntaxError: invalid syntax
    # >>> lambda: (x = 0)
    #   File "<stdin>", line 1
    #     lambda: (x = 0)
    #                ^
    # SyntaxError: invalid syntax

    # ^^ means my mental parsing rule for python "everything (ignoring a few precedence issues) that follows 'lambda:' is the lambda body" is even more wrong in the prescence of type annotatios

    # if sticking with lower prec:
    # x : int = 0  # codegen: x int = 0   # any easy to make gotchas that generate compilable c++?

    # "typed identifier means declaration" would allow explicit
    # {} : x : int
    # int x {}
    # above would be silly because
    # x = {} : int
    # would (when implemented) be valid syntax

    # but for (unfortunate) cases where direct-list-initialization differs from copy-list-initialization
    # could write {1, 2} : x: my_bad_vector<int>
    # https://stackoverflow.com/questions/50422129/differences-between-direct-list-initialization-and-copy-list-initialization



    # prev notes on considering a colon op with lower precedence than = to allow
    # for more common x:int = 0 notation:

        # if ((x = 2): (y = 1) else: (y = 2))  # if ':' had higher precedence
        # if (x == 2: (y = 1) else: (y = 2))   # if ':' has lower precedence than '==' but not '='  (then it's a bug to change a comparison to assign by simply deleting one '=')
        # later note: not a bug, this gives us the "must overparenthesize assignment as if cond" logic for free

        # if (x == 2: y = 1, elif: x == 3: y = 2, else: y = 3)
        # if (x == 2: y = 1, elif: x == 3: y = 2, else: y = 3)

    # bad idea for rewrite rules (if not equiv to precedence change requires maintaining a list of return like operators (on which to avoid rewrite))

    # x : int : const = 5
    # parsed with low precedence ':' is
    # x: (int:(const = 5))
    # algo
    # find x : (int = 0)
    # rewrite as
    # x = 0 : int
    # or as
    # (x:int) = 0
    # find "int: (const = x)"
    # rewrite as ...
    # (int:const) = x
    # so if find
    # x: (int : (const = 5))
    # rewrite to
    # x: ((int:const) = 5)
    # rewrite to
    # (x: (int:const)) = 5

    # should work? but same as simply changing the precedence...
    # same issue with return: x = 5 becomes (return:x)=5


    c = compile(r"""

    
def (foo:
    x = 2
    if (x==1:
        pass
    elif (x = 3):
        std.cout << "ok"
    )
    if (x == 2: pass elif x == 3: std.cout << "ok2")
    if (x == 2: pass elif x == 3: (return 5))
    if (x == 2: pass elif x == 3: 
        return: 1
    )
    return: x = 2
    
    z = x = 10
    
    return: z = 10
)

def (main:
    std.cout << foo()
    x : int = 5
    y : const:int:ref = x
    y2 = x : const:int:ref 
    
    y3 : ((const:int:ref) = x)
    return : (x = 0)
    (return : x) = 0
    
    std.cout << x << y
    # return: z:int = 0
)
    """)

    # assert c == "okok2555"


def test_left_assoc_attrib_access():
    c = compile(r"""
    
class (Foo:
    a
    b
    c
) 

# TODO: should just use auto parameters template syntax always (c++20)
# def (foo, x: auto:
#     pass
# )
    
def (main:
    f = Foo(1, 2, Foo(1, Foo(1, 2, Foo(1,2,3001)), Foo(1,2,3)))
    std.cout << f.c.b.c.c
)
    """)

    assert c == "3001"


@pytest.mark.xfail(sys.platform == "win32", reason="msvc bug")
def test_class_with_attributes_of_generic_class_type():
    # g++ 11.3 some debian unstable: missing deduction guide. works in 12+ and 11.3 godbolt version
    # msvc 19 /std:c++20 or latest: <source>(53): error C2641: cannot deduce template arguments for 'Bar'

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
    f : Foo<decltype(a), decltype(b), decltype(b)>
)

class (Bar2:
    a
    b
    f : decltype(Foo(b,b,b))  # this is probably more intuitive than explicit template syntax although produces wackier looking but equivalent c++ code (either way both cases work)
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
    b = Bar(1, 2, f)
    std.cout << b.a << b.b << b.f.a << b.f.b << b.f.c << "\n"
    b2 = Bar2("hi", 2, Foo(2,3,4))  # should work
    std.cout << b2.a << b2.b << b2.f.a << b2.f.b << b2.f.c << "\n"
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

    assert c.strip() == "3001\n12123\nhi2234\ne2"



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
    f5 = Foo(1, 2, Foo(1, Foo(1, 2, Foo(1,2,3001)), Foo(1,2,3)))
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
def (main, argc:int, argv:char:ptr:ptr:
    # if ((1:int): printf("1") : some_type_lol elif 2 == 4: printf("2") else: printf("3") )
    # if (1:int: printf("1") : some_type_lol elif 2 == 4: printf("2") else: printf("3") )   # warning: declaration does not declare anything:  int;
    # ^ we no longer discard types on non-assignment expressions (now printed as var declarations)
    
    # with '=' lower precedence than ':'
    if ((x = 5): printf("%d", x), elif: argc == 1: printf("1"), elif: (y = 5): printf("unreachable %d", y), else: (z = 10))
)
    """)

    assert c == "5"


def test_generic_refs_etc():
    c = compile(r"""
    
# def (foo, x: auto: ref:  #  error: 'auto' not allowed in function prototype
# def (foo, x: ref:  # should work (stay in template generation mode)
def (foo, x:
    return x
)
    
def (main:
    x = 1
    xref:auto:ref = x # TODO auto inject auto in the local var case
    y: const : auto = 2 
    z : const : auto : ref = 3
    # w : const : ref : auto = 4#   const & auto w = 4;   # not valid c++ syntax
    
    r : const : int : ref = xref
    r2 : int : const : ref = xref
    # r : ref = xref
    
    # p : ptr = 0 # generating "*p = 0;" is bad
    p:const:auto:ptr = &x
    p2: const:auto:ptr:ptr = &p
    p3: int:const:ptr = &x
    # p4 : const:ptr:int = &x #  const * int p4 = (&x);  error expected unqualifief id
    
    
    # These are all bad ideas (we don't / no plans to support these 'conveniences')  (ptr and ref will eventually
    # w1 : ref = x # really auto:ref
    # w2 : const:ref = x # const:auto:ref
    # w3 : ptr = &x # auto:ptr
    # w4 : const:ptr = &x # const:auto:ptr
    
    # rules:  # have to look at outer expression node...
    # see ptr - output auto*
    # see const:ptr - output const auto* 
    
    foo(1)
)
    """)


def test_py14_map_example():
    c = compile(r"""
def (map, values, fun:
    results : mut = []
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
    map(map(l, lambda (x:
        std.cout << x
        x*2
    )), lambda (x:
        std.cout << x
        x
    ))
    map(l, foo)
    # map(l, foo_generic)  # error
    map(l, lambda (x:int, foo_generic(x)))  # when lambda arg is typed, clang 14 -O3 produces same code as passing foo_generic<int>)
    map(l, lambda (x, foo_generic(x)))  # Although we can trick c++ into deducing the correct type for x here clang 14 -O3 produces seemingly worse code than passing foo_generic<int> directly. 
    map(l, foo_generic<int>)  # explicit template syntax
)
	""")

    assert c == "123424681234123412341234"


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
    import subprocess
    if "clang version 11.0.0" in subprocess.getoutput("clang -v"):
        return

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
    assert(std.string(argv.unsafe_at(0)).length() > 0)
    
    lst = ["hello", "world"] 
    foo(lst)
    bar(lst.size())
)
    """)

    assert c.strip() == """
argc 1
size: 2
hello
world
int by const ref 2
    """.strip()


def test_for_scope():
    c = compile("""
def (main:
    x = 5
    
    l : mut = [1,2,3]
    for (x:auto:rref in l:  # note the context sensitivity disguised by a post parse fixup (ordinarily ':' has a lower precedence than 'in')
        x = x + 1
    )
    
    for (x in l:
        printf("%d", x)
    )
    
    for ((x:auto:rref) in [1, 2, 3]:
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
    return  # allow c++17 at least on Mac for now
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
    printf("addr %p\n", static_cast<const:void:ptr>((&b)->get())) # cheat the template magic to get the real shared_ptr (or rather a pointer to it)
    # printf("addr %p\n", (&b).get()) # woo hoo this no longer works! (we previously autoderefed _every_ pointer on every attribute access...)
    # printf("addr temp %p\n", (&Blah())->get())  #  error: taking the address of a temporary object of type 'typename enable_if<!is_array<Blah> ... - good error
    # printf("use_count %ld\n", (&b).use_count())  # no autoderef for arbitrary pointers!
    printf("use_count %ld\n", (&b)->use_count())
    b_addr = &b
    printf("addr of shared_ptr instance %p\n", static_cast<const:void:ptr>(b_addr))
    # printf("addr %p\n", b_addr.get()) # correct error
    printf("addr %p\n", static_cast<const:void:ptr>(b_addr->get()))
    # printf("use_count %ld\n", b_addr.use_count()) # correct error
    printf("use_count %ld\n", b_addr->use_count())
    (*b_addr).huh() # note *b_addr is a shared_ptr<Blah> so accessing via '.' already does deref magic (it's fine)
    (*b_addr)->huh()   # no deref magic is performed here (though arguably bad style)
)
    """)

    assert c.count("huh") == 5


# TODO c-style for loops:
# for (x = 0, x < 10, x+= 1:
#     pass
# )
#for (,true,):  # error not enough for args
#    pass
#)
#for (void(), true, void():  # if you really must have an empty for loop (loop condition required)
#    pass
#)


def test_for_with_uniq_and_shared():
    c = compile(r"""

class (Uniq:
    x = 0

    def (bar: mut:
        self.x = self.x + 1
        printf("in bar %d %p\n", self.x, static_cast<const:void:ptr>(this))
        return self.x
        # just ensure the manual approach compiles too (unreachable):
        this->x = this->x + 1
        printf("in bar %d %p\n", this->x, static_cast<const:void:ptr>(this))
        return this->x
    )
): unique

class (Shared:
    x = 0

    def (foo:
        printf("foo\n")
        return 10
    )
)

def (main:
    x = 5
    for (x:auto:rref in [1, 2, 3]:
        printf("%d\n", x)
        x = x + 1
    )
    
    static_assert(std.is_const_v<decltype(x)>)
    
    lst : mut = [1,2,3]
    for (x:auto:rref in lst:
        printf("%d\n", x)
        x = x + 1
    )
    for (x:auto:rref in lst:
        printf("%d\n", x)
        x = x + 1
    )
    
    u : mut = []
    s : mut = []
    for (x in [1, 2, 3, 4, 5]:
        u.append(Uniq() : mut)
        s.append(Shared())
    )
    
    for (x in u:
        printf("%d\n", x->bar())  # should not be encouraged
        printf("%d\n", x.bar())
        # zz = x # correct error
    )
    
    n : mut:int = 0
    for (x in u:
        printf("bar again: %d\n", x.bar())
        # zz = x # correct error
        # x = Uniq()
        n = n + 1
        if (n % 2 == 0:
            x.bar()
        )
    )
    for (x in u:
        printf("bar again again: %d\n", x.bar())
        # zz = x # correct error
        # x = Uniq()
    )
    
    # v = [] #fix decltype(i)
    v : mut = [Shared() : mut]
    v2 : mut = [Shared()]
    
    for (i in s:
        i.foo()
        # n = i
        # v.append(i)  # error (i is const v contains mut elems)
        v2.append(i) # v2 is not const, contains const elemens
    )
    
    for (vv2 in v2:
        vv2.foo()
    )
    
    s1 = Shared() : mut
    
    for (v1 in v:
        v1.x = 55
        
        std.cout << "v:" << v1.foo()
        # v1 = s1
    )
)
    """)


def test_uniq_ptr():
    c = compile(r"""
class (Foo:
    a:int = 5
    
    def (bar:
        printf("bar %d\n", self.a)
        return self.a
    )
): unique

def (bam, f: Foo:
    f.bar()
)

def (baz, f: Foo:
    f.bar()
    bam(f)  # last use automoved
)

def (main:
    Foo().bar()
    
    baz(Foo())

    f : mut = Foo()
    f.bar()

    f2 : mut = Foo()
    f2.bar()

    # baz(std.move(f2))  # this is no longer necessary
    baz(f2)  # automatic move from last use

    # lst = [Foo(), Foo(), Foo()]  # pfft https://stackoverflow.com/questions/46737054/vectorunique-ptra-using-initialization-list
    lst : mut = []
    lst.append(Foo() : mut)
    f = Foo() : mut
    # lst.append(std.move(f))  # no longer necessary
    lst.append(f)

    lst[0].bar()
    lst[1].bar()
)
    """)

    assert c == r"""
bar 5
bar 5
bar 5
bar 5
bar 5
bar 5
bar 5
bar 5
bar 5
    """.strip() + "\n"


def test_reset_ptr():

    # of course overriding == for the shared_ptr type (taking dubious care not to step on nullptr-checks)
    # should be avoided in the normal course of things
    c = compile(r"""
class (Foo:
    # x = 0  # this is now const by default
    x : int = 0  # TODO this should be too

    def (bar:
        printf("bar %d\n", self.x)
    )
    
    def (destruct:
        printf("dead\n")
    )
    
    def (operator("=="), other: Foo:
        printf("in == method - both foo\n")
        return self.x == other.x
    )
    def (operator("=="), other:
        printf("in == method - other not foo\n")
        return other == 5
    )
)

def (operator("=="), f: Foo, other:
    return f.operator("==")(other)
)
def (operator("=="), f: Foo, otherfoo: Foo:
    return f.operator("==")(otherfoo)
)

def (operator("=="), f: Foo, other: std.nullptr_t:   # "fix" (?) use of overloaded operator '==' is ambiguous
    return not f
    #return f.operator("==")(other)
    #return nullptr == f   # this is no longer possible in c++20 due to the symmetric binary operator reversing scheme (though clang++ on linux seems to accept it)
)

def (main:
    # f:mut = Foo()  # regardless of the reset case below, getting the above overloading to work for mut case is now problematic after 'func params const by default' (probably this whole approach of overriding free standing func operators on the shared_ptrs is problematic)
    f = Foo()
    f.bar()
    if (f == 5:
        printf("overload == works\n")
    )
    # b:mut = Foo()
    b = Foo()
    if (f == b:
        printf("same\n")
    else:
        printf("not same\n")
    )
    # f = nullptr
    # b = nullptr
    f2 : Foo = nullptr
    printf("testing for null...\n")
    if (f2 == nullptr:
        printf("we're dead\n")
    )
    
    if (not f2:
        printf("we're dead\n")
    )
)
    """)


    assert c.strip() == r"""
bar 0
in == method - other not foo
overload == works
in == method - both foo
same
testing for null...
we're dead
we're dead
dead
dead
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
    f : mut = Foo()
    f.foo()
    f2 : mut = f
    f2.foo()
    std.cout << (&f)->use_count() << std.endl
    std.cout << (&f2)->use_count() << std.endl
    f2 = nullptr
    f = nullptr
    printf("f %d\n", not f)
    printf("f2 %d\n", not f2)
    std.cout << (&f)->use_count() << std.endl
    std.cout << (&f2)->use_count() << std.endl
    # f.foo()  # std::terminate
    # f2.foo() # std::terminate
    f->foo()  # intentional UB
    f2->foo()  # UB
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


@pytest.mark.skipif(sys.platform == "win32", reason="problems with native stack overflow / recursionlimit failing windows ci")
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
    fp2 = fopen("file.txt", "r")
    fclose(fp2)
    
    t = std.ifstream(c"file.txt")
    buffer : mut = std.stringstream()
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
    
    # This may be a bit busy but allows an unambiguous return type
    # def (foo:A, x:A:
    #     printf("Blah1 foo\n")
    #     x.huh()
    # ):int  # or ':A' if it returns an 'A'!
    
    # or explicit interface(A) although meaning of 'A' is clear from scope if already defined (not so much for auto-definition; could also add 'concept' although not sure worth it just to improve C++ compiler error messages)
    
    # We've switched to this which makes "which code uses the interfaces feature" possible via text search
    def (foo:interface(A), x:A:
        printf("Blah1 foo\n")
        return x.huh()
    ):int
    
    # Previous implementation. Totally inconcistent - how to return a shared_ptr<A> ? (that is an A in whatever-lang-called code). You can't! (or rather must hope auto return type deduction suffices!)
    # def (foo, x:A:
    #     printf("Blah1 foo\n")
    #     x.huh()
    # ):int:A  # requires checking that A not in [const, ref, ptr] - not the only problem with this approach ^^ !
    
    def (huh:interface(A):
        printf("huh 1\n")
        return 76
    ):int
    
    # def (huh:A:
        
)

class (Blah2:
    def (foo:interface(A), x:A:
        printf("Blah2 foo\n")
        return x.huh()
    ):int
    
    def (huh:interface(A):
        printf("huh 2\n")
        return 89
    ):int
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
# def (operator("+"), x, y:
#     printf("adding any and any\n")
#     return std.operator("+")(x, y)
# )

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

class (Foo: # this is the parse prob
    # x = 1
    # y = 2
    x = 0

    # def (init:
    #     printf("init\n")
    # )

    def (destruct:
        printf("dead %p\n", static_cast<const:void:ptr>(this))
    )

    def (bar:
        printf("in bar\n")
    )

    def (foo:
        printf("in foo method %p\n", static_cast<const:void:ptr>(this))

        bar()
        self.bar()
        printf("bar attribute access %d\n", self.x)
        printf("bar attribute access %d\n", x)
        # shared_from_base()
        return self
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
    f : mut = Foo()
    f.foo()
    f.x = 55
    f.foo()
    y = Foo()
    calls_foo(y).foo().foo()
)
    """)

    import re
    deadlines = list(re.findall("dead.*", output))
    assert len(deadlines) == 3

    attrib_accesses = list(re.findall("bar attribute access.*", output))
    assert attrib_accesses == ["bar attribute access 0"]*4 + ["bar attribute access 55"]*2 + ["bar attribute access 0"]*6


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
    printf("xxanother2 %d\n", xxanother2[0][0])
    printf("xxanother %d\n", xxanother[0][0])

    lfunc = lambda (x, y, return x + y )
    lfunc2 = lambda (x, y: 
        printf("x %d y %d\n", x, y)
        return x + y 
    )

    huh = takes_func_arg_arg(lfunc2, 14, 15)

    printf("yo:
            %d %d\n", xx3[0][0][0], huh) 
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
    compile(r"""
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
        0
        #printf("%d\n", main)
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

    # most of these "noscope" ifs fail now (for good reasons). TODO just delete this test
    raises(lambda: compile(r"""

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
    """))


def test_append_to_empty_list_type_deduction():
    return
    compile("""
def (almostmap, values, fun:
    results : mut = []
    results.append(fun())
    return results
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
# (sometimes want to bypass pytest for various reasons)
def _run_all_tests(mod):
    import inspect
    all_functions = inspect.getmembers(mod, inspect.isfunction)
    for key, value in all_functions:
        if str(inspect.signature(value)) == "()":
            value()

if __name__ == '__main__':
    import sys

    _run_all_tests(sys.modules[__name__])
    # test_parameter_pack()
    # test_more_conversions()
    # test_forwarder()
    #test_curly_brace()
    # test_std_function()
    # test_if_expressions()
    # test_capture()
    #test_complex_list_typing()
    # test_lambda_unevaluated_context()
    # test_braced_call()
    # test_implicit_conversions()
    # test_curly_brace()
    # test_self_lambda_safe()
    # test_complicated_function_directives()
    # test_range_signedness()
    # test_compound_comparison()
    # test_recur()
    # test_contains_helper2()
    # test_double_angle_close()
    # test_ptr_not_simple_type_context()
    # test_a_andand_b_wrong()
    # test_contains_helper()
    # test_complex_arguments()
    # test_scope_resolution()
    # test_lambda_void_deduction_and_return_types()
    # test_typed_identifiers_as_cpp_variable_declarations()
    # test_manual_implementation_of_proper_refcounted_return_self()
    # test_higher_precedence_colon()
    # test_left_assoc_attrib_access()
    #test_add_stuff()
    # test_class_attributes()
    #test_class_with_attributes_of_generic_class_type()
    # test_generic_refs_etc()
    # test_py14_map_example()
    # test_range_iota()
    # test_complex_arguments()
    # test_for_scope()
    # test_correct_shared_ptr()
    # test_bad_indent()
    # test_for()
    # test_three_way_compare()
    # test_deref_address_of()
    # test_uniq_ptr()
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
