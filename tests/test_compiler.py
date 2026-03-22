import sys
import os
import subprocess

import pytest

from ceto.parser import parse


# these require range_value_t for untyped / forward typed vectors (not worth adding #ifdefs to fallback to using ::value_type - just upgrade your clang)
clang_xfailing_tests = ["atomic_weak.ctp",
                        "tuples_for.ctp",
                        "example.ctp",  # std.span use also fails on apple clang 14
                        "regression/tuples_for_typed.ctp",
                        "regression/range_iota.ctp",
                        "regression/contains_helper.ctp",
                        "regression/attempt_use_after_free2.ctp",  # something about constexpr / std::chrono. This works on debian clang++ 14.0.6 but fails to compile on ci
                        "regression/list_type_on_left_or_right_also_decltype_array_attribute_access.ctp"]

apple_clang_xfailing_tests = [
    "py14_map_example.ctp",  # not sure why this doesn't fail on clang14/15 on linux ci
    "regression/empty_list_append_simple_vector_iterate.ctp"  # same
]

msvc_xfailing_tests = ["regression\\string_escapes_unicode_escape.ctp",
                       "regression\\class_with_attributes_of_generic_class_type.ctp"]

test_file_dir = os.path.dirname(__file__)
test_files = [f for f in os.listdir(test_file_dir) if f.endswith("ctp")]

regression_dir = os.path.join(test_file_dir, "regression")
test_files += [os.path.join("regression", f) for f in os.listdir(regression_dir) if f.endswith("ctp")]

test_files = [f for f in test_files if f not in clang_xfailing_tests and f not in msvc_xfailing_tests and not (sys.platform == "darwin" and f in apple_clang_xfailing_tests)]

for xfailing in clang_xfailing_tests:
    test_files.append(pytest.param(xfailing, marks=pytest.mark.xfail(sys.platform != "win32" and ("clang version 14." in (cv := subprocess.check_output([os.environ.get("CXX", "c++"), "-v"], stderr=subprocess.STDOUT).decode("utf8")) or "clang version 15." in cv), reason="not supported with this clang version")))

if sys.platform == "darwin":
    for xfailing in apple_clang_xfailing_tests:
        test_files.append(pytest.param(xfailing, marks=pytest.mark.xfail(sys.platform == "darwin" and ("clang version 14." in (cv := subprocess.check_output([os.environ.get("CXX", "c++"), "-v"], stderr=subprocess.STDOUT).decode("utf8")) or "clang version 15." in cv), reason="not supported with this clang version")))

if sys.platform == "win32":
    for xfailing in msvc_xfailing_tests:
        test_files.append(pytest.param(xfailing, marks=pytest.mark.xfail(sys.platform == "win32", reason="-")))


def _run_test(file):
    prefix = "# Test Output:"

    path = os.path.join(os.path.dirname(__file__), file)

    with open(path) as f:
        content = f.readlines()
        #content = "unsafe()\n" + content  # below tests not fixed for unsafe

    output_lines = [c[len(prefix):].strip() for c in content if c.startswith(prefix)]

    if output_lines:
        expected_output = "\n".join(output_lines)
    else:
        expected_output = None

    build_command = f"{sys.executable} -m ceto -o a.exe --donotexecute {path}"
    build_output = subprocess.check_output(build_command, shell=True).decode("utf8")

    print(build_output)

    output = subprocess.check_output(os.path.join(os.path.curdir, "a.exe"), shell=True).decode("utf8")

    if sys.platform == "win32":
        output = output.replace("\r\n", "\n")

    print(output)

    if expected_output is not None:
        assert output.strip() == expected_output.strip()

    return output


@pytest.mark.parametrize("file", test_files)
def test_file(file):
    _run_test(file)


def compile(string: str, compile_cpp=True):
    file_path = os.path.join(os.path.dirname(__file__), "testsuitegenerated.ctp")

    with open(file_path, "w") as f:
        f.write("unsafe()\n" + string)  # below compile from string tests not yet fixed with unsafe

    return _run_test(file_path)


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


def test_if_assign_missing_parenthesese():
    raises(lambda:compile(r"""

def (main:
    x:mut = 5
    if (x = 6:
        pass
    )
)
    
"""), exc="assignment in if missing extra parenthesese")

    raises(lambda: compile(r"""

def (main:
    x:mut = 5
    if ((x = 6):
        pass
    elif x = 7:
        pass
    )
)

"""), exc="bad if-arg ((elif : x) = 7) at position 2")

    c = compile(r"""

def (main:
    x:mut = 5
    if ((x = 6):
        pass
    elif (x = 7):
        pass
    )
    std.cout << x
)

""")

    assert c == "6"

    raises(lambda: compile(r"""

def (main:
    x:mut = 5
    if (x = 6: pass)
)

"""), exc="bad first if-args")

    raises(lambda: compile(r"""

def (main:
    x:mut = 5
    if ((x = 6): pass elif x = 7: pass)
)

"""), exc="bad if-arg ((elif : x) = (7 : pass)) at position 2")

    c = compile(r"""
def (main:
    x:mut = 5
    if ((x = 6): pass elif (x = 7): pass )
    if ((x = 8): pass elif (x = 9): pass else: pass)
    std.cout << x
)
""")

    assert c == "8"


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



def test_more_mut_const_declarations_error_cases():
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


def test_better_lambda_error():
    raises(lambda: compile(r"""
def (main:
    lambda(x: x+1)
)
    """), "do you have the args wrong? [ it's lambda(x, 5) not lambda(x: 5) ] ")


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
            self.f.foo(x)
        )
    )

    x = 1
    f = Foo()
    l = lambda (f.foo(x))
    l()  # we avoid an immediatelly invoked lambda (now implicit refcapture) to bump refcount for test
    
    i = Inner(f)
    lambda (i.foo(x)) ()
)
    """)
    assert c == "hi13hihi14dead"

    c = compile(r"""
def (main:
    x = 1
    y : const:int:ref = x  # fine to copy capture
    c = char'A'
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
    x : const:int:ptr:const = &y  # TODO just int:ptr used to work but now doesn't (though multiple mut syntax for pointers arguably should be implemented)

    l = lambda (:
        std.cout << x
        return
    )
    l()  # NOTE: in the event we scan for non-escaping lambdas this may need updating (ref capture would be fine in such a case)
)
        """)
    raises(f2)
    def f3():
        compile(r"""
def (main:
    s = "nope"

    l = lambda (:
        std.cout << s
        return
    )
    l()
)
        """)
    raises(f3)


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


def test_c_array_errors():
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

    # NO (clashes with python list compatibility syntax - C arrays can be introduced via C/C++ preprocessor)
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
