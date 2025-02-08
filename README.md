## Intro

Experimental dialect of C++ with a python ish syntax using infix expressions and function calls (that may optionally take indented blocks) and a python ish reference counted class-semantics (except immutable/const by default). We aspire to a simple "copy it, refcount it, or pass but don't store by const ref" approach to safety (with a few extensions like cppfront inspired move from last use of unique) with static checks, C++ compile time checks and static_asserts, runtime checks, and unsafe blocks for the rest.

```python
# see the tests and selfhost directories for more examples

include <ranges>

unsafe()  # current safe mode (with unsafe blocks) is in progress.
          # add a call to unsafe() to all your modules to avoid churn/breakage or
          # for wrapper free interop with external C++

defmacro ([x, for (y in z), if (c)], x, y, z, c:
    result = gensym()
    zz = gensym()

    pre_reserve_stmt = if (isinstance(c, EqualsCompareOp) and std.ranges.any_of(
                           c.args, lambda(a, a.equals(x) or a.equals(y))):
        # Don't bother pre-reserving a std.size(z) sized vector for simple searches 
        # e.g. [x, for (y in z), if (y == something)]
        dont_reserve: Node = quote(pass)
        dont_reserve
    else:
        reserve: Node = quote(maybe_reserve(unquote(result), unquote(zz)))
        reserve
    )

    return quote(lambda (:

        unquote(result): mut = []  # immutable by default (mostly!), so mark it "mut"

        unquote(zz): mut:auto:ref:ref = unquote(z)  # explicit use of "auto" or "ref" requires
                                                    # an explicit "mut" or "const" annotation.
                                                    # (in addition safe mode bans local variables of reference type) 
        unquote(pre_reserve_stmt)

        for (unquote(y) in unquote(zz):
            unquote(if (c.name() == "True":
                # Omit literal if (True) check (reduce clutter for 2-arg case below)
                quote(unquote(result).append(unquote(x)))
            else:
                quote(if (unquote(c):
                    unquote(result).append(unquote(x))
                ))
            ))
        )

        unquote(result)
    ) ())
)

defmacro ([x, for (y in z)], x, y, z:
    # Use the existing 3-arg definition
    return quote([unquote(x), for (unquote(y) in unquote(z)), if (True)])
)

# metaprogramming in ceto/C++ templates rather than procedural macros is recommended:

def (maybe_reserve<T>, vec: mut:[T]:ref, sized: mut:auto:ref:ref:
    vec.reserve(std.size(std.forward<decltype(sized)>(sized)))
) : void:requires:requires(std.size(sized))

def (maybe_reserve<T>, vec: mut:[T]:ref, unsized: mut:auto:ref:ref:
    pass
) : void:requires:not requires(std.size(unsized))
```

```python
include <ranges>
include <iostream>
include <numeric>
include <future>
include <map>

include (macros_list_comprehension)

class (Foo:
    data_member

    def (method, param:
        std.cout << param.size() << std.endl
        return self  # implicit +1 refcount (shared_from_this)
    )

    def (size:
        return self.data_member.size()
    )
)

def (calls_method, arg:
    return arg.method(arg)
)

# Unique classes are implicitly managed by std.unique_ptr and use cppfront inspired 
# move from last use. Instance variables may be reassigned (allowing implicit move) but 
# point to immutable instances (aka unique_ptr to const by default)

class (UniqueFoo:
    consumed: [UniqueFoo] = []

    def (size:
        return self.consumed.size()
    )
    
    # For all classes and structs, a method that mutates its data members must be "mut".
    # Note that "u" is a passed by value std::unique_ptr<const UniqueFoo> in C++
    def (consuming_method: mut, u: UniqueFoo:
        
        # u.consuming_method(None)  # Compile time error:
        # "u" is not a UniqueFoo:mut so a "mut" method call is banned

        # "u" is passed by reference to const to the generic method "method" here.
        Foo(42).method(u)

        self.consumed.append(u)  # Ownership transfer of "u" on last use (implicit std.move)
    )
) : unique

# std.string and vectors (implicit use of std.vector with square brackets) passed 
# by reference to const by default:
def (string_join, vec: [std.string], sep = ", "s:
    if (vec.empty():
        return ""
    )
    unsafe (:
        return std.accumulate(vec.cbegin() + 1, vec.cend(), vec[0],
            lambda[&sep] (a, b, a + sep + b))
    )
): std.string

# defmacro param types use the ast Node subclasses defined in selfhost/ast.cth

defmacro (s.join(v), s: StringLiteral, v:
    return quote(string_join(unquote(v), unquote(s)))
)

def (main, argc: int, argv: const:char:ptr:const:ptr:

    # macro invocations:
    args = [std.string(a), for (a in unsafe(std.span(argv, argc)))]
    summary = ", ".join(args)

    f = Foo(summary)  # implicit make_shared / extra CTAD:
                      # in C++ f is a const std::shared_ptr<const Foo<decltype(summary)>>

    f.method(args)    # autoderef of f
    f.method(f)       # autoderef also in the body of 'method'
    calls_method(f)   # autoderef in the body of calls_method (and method)

    fut: mut = unsafe(std.async(std.launch.async, lambda(:

        # Implicit copy capture (no capture list specified) for shared/weak
        # ceto-class instances, arithmetic types, and enums only (even in unsafe blocks).

        f.method(f).data_member
    )))

    std.cout << fut.get()

    u: mut = UniqueFoo()    # u is a "non-const" std::unique_ptr<non-const UniqueFoo> in C++
    u2 = UniqueFoo()        # u2 is a non-const std::unique_ptr<const UniqueFoo> in C++

    u.consuming_method(u2)  # Implicit std.move from last use of u2.
                            # :unique are non-const (allowing move) but
                            # unique_ptr-to-const by default.

    u.consuming_method(u)   # in C++: CETO_AUTODEREF(u).consuming_method(std::move(u))
)
```

## Usage

```bash
$ git clone https://github.com/ehren/ceto.git
$ cd ceto
$ pip install .
$ ceto ./tests/example.ctp a b c
```

### Continued Intro

While you can express a great deal of existing C++ constructs in ceto code (you can even write ceto macros that output, and rely on for their compiled to DLL implementation, a mix of C++ template and C/C++ preprocessor metaprogramming - or even other ceto macros!) the emphasis is not on system programming but more so called "Pythonic glue code" (whether it's a good idea to write such code in C++ to begin with). One should be able to translate ordinary Python code to pythonic ceto just by adding the necessary parenthesese and viral ```:mut``` annotations but without worrying about additional complicated parameter passing rules, explicit reference/pointer type annotations, nor call site referencing/dereferencing syntax. While e.g. the keywords ```ref```, ```ptr``` and operator ```->``` and unary operators```*``` and ```&``` exist in ceto (for expressing native C++ constructs and interfacing with external C++) they should be regarded as constituents of a disconnected low level subset of the language that will even TODO require explicit ```unsafe``` blocks/contexts in the future. Though, lacking a complete ```unsafe``` blocks implementation, current ceto should be regarded as *unsafe ceto*, runtime safety checks are nevertheless performed for pythonic looking code: ```.``` (when a smart pointer or optional deref) is null checked and ```array[index]``` is runtime bounds checked when array is a contiguous container (the technique of checking if std::size is available for ```array``` using a ceto/C++ ```requires``` clause before inserting a runtime bounds check has been taken from Herb Sutter's cppfront - see include/boundscheck.cth).

### More Features:

- reference to const and value semantics emphasized.
- Python like class system but immutable by default (more like an immutable by default Java halfway naively implemented with std::shared_ptr and std::enable_shared_from_this).
- structs passed by reference to const by default, by value if just "mut" (raw pointers or references allowed via ref or ptr keywords but may be relegated to unsafe blocks in the future)
- Implicit swiftish lambda capture
- Implicit move from last use of unique (and TODO non-class mut)
- non-type annotated "Python" == unconstrained C++ function and class templates
- extra CTAD

## Features Explanation

### Autoderef (use *.* not *->*)

This works by compiling a generic / non-type-annotated function like

```python
def (calls_foo, f:
    return f.foo()
)
```

to the C++ template function

```c++
#include <ceto.h>

auto calls_foo(const auto& f) -> auto {
    return (*ceto::mad(f)).foo();
}
```

where `ceto::mad` (maybe allow dereference) amounts to just `f` (allowing the dereference via `*` to proceed) when `f` is a smart pointer or optional, otherwise returning the `std::addressof` of `f` to cancel the dereference for anything else (more or less equivalent to ordinary attribute access `f.foo()` in C++). This is adapted from this answer: https://stackoverflow.com/questions/14466620/c-template-specialization-calling-methods-on-types-that-could-be-pointers-or/14466705#14466705 except the ceto implementation (see include/ceto.h) avoids raw pointer autoderef (you may still use `*` and `->` when working with raw pointers). When `ceto::mad` allows a dereference, it also performs a terminating nullptr check (use `->` for an unsafe unchecked access).

### Less typing (at least as in your input device\*)

This project uses many of the ideas from the wonderful https://github.com/lukasmartinelli/py14 project such as the implicit insertion of *auto* (though in ceto it's implict *const auto* for untyped locals and *const auto&* for untyped params). The very notion of generic python functions as C++ template functions is also largely the same.

We've also derived our code generation of Python like lists as *std.vector* from the project.

For example, from [their README](https://github.com/lukasmartinelli/py14?tab=readme-ov-file#how-it-works):

```python
# Test Output: 123424681234123412341234


def (map, values, fun:
    results: mut = []
    for (v in values:  # implicit const auto&
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
    l = [1, 2, 3, 4]  # definition simply via CTAD (unavailable to py14)
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
```

Though, we require a *mut* annotation and rely on *std.ranges*, the wacky forward inference via *decltype* to codegen the type of results above as *std::vector<decltype(fun(std::declval<std::ranges::range_value_t<decltype(values)>>()))>* derives from the py14 implementation.

(*tempered with the dubiously attainable goal of less typing in the language implementation)

### Classes, Inheritance

Class definitions are intended to resemble Python dataclasses

```python
# Test Output: 5555.0one

include <map>
include <string>

class (Generic:
    x  # implicit 1-arg constructor, deleted 0-arg constructor
)

class (Concrete(Generic):
    def (init, x: int:
        super.init(x)
    )
)

class (Generic2(Generic):
    y
    def (init, x, y:
        self.y = y
        super.init(x)
    )
)

class (Concrete2(Concrete):
    # no user defined init - inherits constructors
    pass
)

def (main:
    f = Generic("5")
    f2 = Concrete(5)
    #f2e = Concrete("5")  # error
    f3 = Generic2([5, 6], std.map<int, std.string> { {1, "one"} })
    f4 = Concrete2(42)
    std.cout << f.x << f2.x << f3.x[0] << f3.y.at(1) << f4.x
)
```

### Tuples, "tuple unpacking" (std::tuple / structured bindings / std::tie)

```python
# Test Output: 01
# Test Output: 12
# Test Output: 23
# Test Output: 34
# Test Output: 00
# Test Output: 56
# Test Output: 12
# Test Output: 71
# Test Output: 89
# Test Output: 910
# Test Output: 01

include <ranges>
include <iostream>

def (foo, tuple1: (int, int), tuple2 = (0, 1):
    # TODO perhaps Python like tuple1[0] notation for transpiler known tuples
    return (std.get<0>(tuple1), std.get<1>(tuple2))
)

def (main:
    tuples: mut = []

    for (i in std.ranges.iota_view(0, 10):
        tuples.append((i, i + 1))
    )

    (a, b) = (tuples[0], tuples[1])
    tuples.append(a)

    (tuples[4], tuples[6]) = ((0, 0), b)

    (std.get<0>(tuples[7]), std.get<1>(tuples[7])) = foo(tuples[7])

    for ((x, y) in tuples:  # const auto&
        std.cout << x << y << "\n"
    )

    for ((x, y):mut:auto:ref in tuples:  # auto&
        x += 1
        y += 2
    )

    for ((x, y):mut in tuples:  # just auto
        static_assert(std.is_same_v<decltype(x), int>)
        static_assert(std.is_same_v<decltype(y), int>)
    )
)
```

### Shared / weak

```python

# Test Output: action
# Test Output: action
# Test Output: action
# Test Output: Delegate destruct
# Test Output: Timer destruct

include <thread>

class (Delegate:
    def (action:
        std.cout << "action\n"
    )

    def (destruct:
        std.cout << "Delegate destruct\n"
    )
)

class (Timer:
    _delegate: Delegate

    _thread: std.thread = {}

    def (start: mut:
        w: weak:Delegate = self._delegate

        self._thread = std.thread(lambda(:
            while (True:
                std.this_thread.sleep_for(std.chrono.seconds(1))
                if ((s = w.lock()):  # implicit capture of "w"
                    s.action()
                else:
                    break
                )
            )
        ))
    )

    def (join: mut:
        self._thread.join()
    )

    def (clear_delegate: mut:
        self._delegate = None
    )

    def (destruct:
        std.cout << "Timer destruct\n"
    )
)

def (main:
    timer: mut = Timer(Delegate())
    timer.start()

    std.literals: using:namespace
    std.this_thread.sleep_for(3.5s)

    timer.clear_delegate()
    timer.join()
)
```

### Simple Visitor

This example demonstrates non-trivial use of self and mutable ceto-class instances

```python
class (Node)
class (Identifier)
class (BinOp)
class (Add)

class (Visitor:

    def (visit: virtual:mut, node: Node): void = 0

    def (visit: virtual:mut, node: Identifier): void = 0

    def (visit: virtual:mut, node: BinOp): void = 0

    def (visit: virtual:mut, node: Add): void = 0
)

class (Node:
    loc : int

    def (accept: virtual, visitor: Visitor:mut:
        visitor.visit(self)
    )
)

class (Identifier(Node):
    name : std.string

    def (init, name, loc=0:
        # a user defined constructor is present - 1-arg constructor of Node is not inherited
        self.name = name  # implicitly occurs in initializer list
        super.init(loc)   # same
    )

    def (accept: override, visitor: Visitor:mut:
        visitor.visit(self)
    )
)

class (BinOp(Node):
    args : [Node]

    def (init, args, loc=0:
        self.args = args
        super.init(loc)
    )

    # Note the virality of mut annotations:
    # (visitor must be a mut:Visitor because visit modifies the data member "record")

    def (accept: override, visitor: Visitor:mut:
        visitor.visit(self)
    )
)

class (Add(BinOp):
    # inherits 2-arg constructor from BinOp (because no user defined init is present)

    def (accept: override, visitor: Visitor:mut:
        visitor.visit(self)
    )
)

class (SimpleVisitor(Visitor):
    record = s""

    def (visit: override:mut, node: Node:
        self.record += "visiting Node\n"
    )

    def (visit: override:mut, ident: Identifier:
        self.record += "visiting Identifier " + ident.name + "\n"
    )

    def (visit: override:mut, node: BinOp:
        self.record += "visiting BinOp\n"

        for (arg in node.args:
            arg.accept(self)  # non-trivial use of self (hidden shared_from_this)
        )
    )

    def (visit: override:mut, node: Add:
        self.record += "visiting Add\n"

        for (arg in node.args:
            arg.accept(self)
        )
    )
)

def (main:
    node = Node(0)
    ident = Identifier("a", 5)
    args: [Node] = [ident, node, ident]
    add: Add = Add(args)

    simple_visitor: mut = SimpleVisitor()
    ident.accept(simple_visitor)
    add.accept(simple_visitor)

    std.cout << simple_visitor.record
)

# Output:
# visiting Identifier a
# visiting Add
# visiting Identifier a
# visiting Node
# visiting Identifier a
```

Note that this example illustrates mutable class instance variables, especially as
function parameters e.g. ```visitor``` of ```accept```.  However, compared to 
idiomatic C++ code, there is a considerable runtime overhead (though some safety benefits) in making
```Visitor``` and ```SimpleVisitor``` ceto-classes rather than ceto-structs (see below).

In selfhost/ast.cth and selfhost/visitor.cth, ```Visitor``` is defined as a ```struct``` and
the ```accept``` methods take ```visitor``` by ```mut:ref```:

So, for example, the top level ast node ```Module``` is defined in selfhost/ast.cth as:

```python
class (Module(Block):
    has_main_function = False

    def (accept: override, visitor: Visitor:mut:ref:
        visitor.visit(*this)
    )

    def (clone: override:
        c: mut = Module(self.cloned_args(), self.source)
        return c
    ) : Node:mut
)
```

This ```accept``` has better runtime perforance than ```SimpleVisitor```'s class heavy version above but 
note that raw pointer dereference e.g. ```*this``` and mutable C++ references in
function params (and elsewhere!) should be / will be TODO relegated to unsafe blocks!

### struct

"The struct is a class notion is what has stopped C++ from drifting into becoming a much higher level language with a disconnected low-level subset." - Bjarne Stroustrup

```python

include<string>

struct (Foo:
    x: std.string
)

def (by_const_ref, f: Foo:  # pass by const ref
    static_assert(std.is_same_v<decltype(f), const:Foo:ref>)
    static_assert(std.is_reference_v<decltype(f)>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(f)>>)
    std.cout << f.x
)

def (by_val, f: Foo:mut:  # pass by value (mut:Foo also fine)
    static_assert(std.is_same_v<decltype(f), Foo>)
    static_assert(not std.is_reference_v<decltype(f)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(f)>>)
    std.cout << f.x
)

def (by_const_val, f: Foo:const:  # pass by const value (west const also acceptable)
    # TODO this should perhaps be pass by const ref instead (or an error!) - bit of a perf gotcha. Same problem with std.string and [T])
    # Note that for the class case - Foo and Foo:mut are both passed by const ref (to shared_ptr)
    static_assert(std.is_same_v<decltype(f), const:Foo>)
    static_assert(not std.is_reference_v<decltype(f)>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(f)>>)
    std.cout << f.x
)

def (by_mut_ref, f: Foo:ref:mut:  # pass by non-const reference (mut:Foo:ref also fine - west mut)
    static_assert(std.is_same_v<decltype(f), Foo:ref>)
    static_assert(std.is_reference_v<decltype(f)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(f)>>)
    f.x += "hi"
    std.cout << f.x
)

# TODO: Note that using fully notated const pointers like below is recommended for all ceto code. 
# The const by default (unless :unique) for function parameters feature behaves a bit like add_const_t currently
# (the multiple mut syntax "mut:Foo:ptr:mut" is not even currently supported for Foo** in C++ -
#  while mut:Foo:ptr or Foo:ptr:mut works currently, future ceto versions may require additional mut/const annotations)
def (by_ptr, f: const:Foo:ptr:const:
    static_assert(std.is_same_v<decltype(f), const:Foo:ptr:const>)
    std.cout << f->x  # no autoderef for raw pointers
)

def (main:
    f = Foo("blah")
    by_const_ref(f)
    by_val(f)
    by_const_val(f)
    # by_mut_ref(f)  # error: binding reference of type ‘Foo&’ to ‘const Foo’ discards qualifiers
    fm : mut = f  # copy
    by_mut_ref(fm)
    by_ptr(&f)
)
```

### std.optional autoderef

In this example, ```optional_map.begin()``` suffices where C++ would require ```optional_map.value().begin()```:

```python
include <iostream>
include <map>
include <optional>

def (main:
    optional_map: std.optional<std.map<std.string, int>> = std.map<std.string, int> {
        {"zero", 0}, {"one", 1}}

    if (optional_map:
        updated: mut:std.map<std.string, int> = {{ "two", 2}}

        # Autoderef
        updated.insert(optional_map.begin(), optional_map.end())

        updated["three"] = 3
        for ((key, value) in updated:
            std.cout << key << value
        )
    )
)
```

For ```std.optional``` instances, no deref takes place when calling a method of ```std.optional```. That is, to call a method `value()` on the underlying value rather than the optional call `.value().value()`.

(this example also illustrates that for ceto classes and structs round parenthese must be used e.g.  ```Foo(x, y)``` even though the generated code makes use of curlies e.g. ```Foo{x, y}``` (to avoid narrowing conversions). For external C++ round means round - curly means curly (```std.vector<int>(50, 50)``` is a 50 element vector of 50)

### Evading autoderef

In contrast to the behavior of optionals above, for "class instances" or even explicit std.shared/unique_ptrs you must use a construct like 

```python
(&o)->get()
```

to get around the autoderef system and call the smart ptr `get` method (rather than a `get` method on the autoderefed instance).

Complete example:

```python
class (Foo:
    def (bar:
        std.cout << (&self)->use_count()             # +1 to use_count (non-trivial use of self)
        std.cout << lambda((&self)->use_count()) ()  # +1 copy capture of self
                                                     # note: this capture requires a lambda[&this] capture list
    )
)

def (main:
    f = Foo()
    f.bar()

    (refcount, addr) = lambda (:
        ((&f)->use_count(), (&f)->get())  # +1 copy capture of f
    ) ()

    std.cout << refcount << addr->bar()
)
```

Requiring the `&` and `->` syntax in these cases has the added benefit of signaling unsafety (a fully safe ceto would require no additional logic to ban all potentially unsafe use of smart pointer member functions outside of unsafe blocks: they're banned automatically by banning any occurence of operators ```*```, ```&```, and ```->``` outside of unsafe blocks).

### C++ templates

Writing simple templates can be achieved by Python style "generic" functions (see the first example). Explicit C++ template functions, classes, and variables may still be written:

```python
include <ranges>
include <algorithm>

namespace(myproject.utils)  # everything that follows (in this file only) is defined in this C++ namespace

# explicit template function
def (range: template<typename:...:Args>, args: mut:Args:rref:...:
    if ((sizeof...)(Args) == 1:
        zero : typename:std.tuple_element<0, std.tuple<Args...>>::type = 0
        return std.ranges.iota_view(zero, std.forward<Args>(args)...)
    else:
        return std.ranges.iota_view(std.forward<Args>(args)...)
    ) : constexpr
) : decltype(auto)

# generic "Python" style function (container is const auto&)
def (contains, container, element: const:typename:std.remove_reference_t<decltype(container)>::value_type:ref:
    return std.find(container.cbegin(), container.cend(), element) != container.cend()
)

# additional nested namespaces require a block:
namespace(extra.detail:

    # template variable example from https://stackoverflow.com/questions/69785562/c-map-and-unordered-map-template-parameter-check-for-common-behavior-using-c/69869007#69869007
    is_map_type: template<class:T>:concept = std.same_as<typename:T.value_type, std.pair<const:typename:T.key_type, typename:T.mapped_type>>
)
```

Assuming the above is written to a file myprojectutils.cth, we can include it:

```python
include <map>
include (myprojectutils)

def (main:
    for (x in myproject.utils.range(5, 10):
        if (myproject.utils.contains([2, 4, 6], x):
            std.cout << x
        )
    )

    m: std.unordered_map<string, int> = {}
    static_assert(myproject.utils.extra.detail.is_map_type<decltype(m)>)
)
```

### Macros

Macros should be used sparingly for extending the language. When possible, C++ templates or preprocessor macros should be preferred.

Macros are unhygienic (use gensym for locals to avoid horrific capture bugs). Automatic hygiene at least for simple local variables as well as automatic unquoting of params might be implemented in the future.

Continuing with our example of ```pyprojectutils.cth```, we can create a header called ```incontains.cth```:

```python
include (myprojectutils)

defmacro(a in b, a, b:
    if ((call = asinstance(a.parent().parent(), Call)):
        if (call.func.name() == "for":
            # don't rewrite the "in" of a for-in loop (pitfall of a general syntax!)
            return None
        )
    )

    # std.ranges.contains would be better if you're using c++23
    return quote(myproject.utils.contains(unquote(b), unquote(a)))
)
```

and include it:

```python
include <iostream>
include (incontains)
include (myprojectutils)  # unnecessary because incontains.cth already includes 
                          # (but good style to include what you use)

def (main:
    for (x in myproject.utils.range(10):
        if (x in [2, 4, 6]:
            std.cout << x
        )
    )
)
```

Once std.ranges.contains is accepted on all github actions runners in c++23 mode, we'll likely add our in-macro as a built-in. Note that redefining macros is acceptable (the latest definition in scope gets the first attempt at a match).

#### Alternational arguments

We can't dynamically redefine integer constants like Python (https://hforsten.com/redefining-the-number-2-in-python.html) but the next best thing is possible if not recommended:

```python
# Test Output: 1
# Test Output: 2
# Test Output: 1.5
# Test Output: 1.6

include <iostream>
include <cstdlib>

defmacro (a, a: IntegerLiteral|FloatLiteral:

    # getting at the alternatives requires downcasting
    # ('match' syntax and defmacro(..., elif ..., else, ...) a future possibility)
    if ((i = asinstance(a, IntegerLiteral)):
        if (i.integer_string == "2":
            # 2 is 1
            return quote(1)
        )
    else:
        f = asinstance(a, FloatLiteral)
        d = std.strtod(f.float_string.c_str(), nullptr)
        if (d >= 2.0 and d <= 3.0:
            # subtract 0.5 for kicks
            suffix = quote(l)
            n = FloatLiteral(std.to_string(d - 0.5), suffix)
            return n
        )
    )

    return None
)

def (main:
    std.cout << 2 << "\n"
    std.cout << 2 + 1 << "\n"
    std.cout << 1.5 << "\n"
    std.cout << 2.5 + 0.1 << "\n"  # Macro expansion iterates to a fixed point:
                                   # One application rewrites 2.5 to 2.0f, a second to 1.5f; no changes on third pass
)
```

#### Variadic arguments

```python
include <ranges>
include <iostream>

defmacro (summation(args), args: [Node]:
    if (not args.size():
        return quote(0)
    )

    if (defined(__clang__) and __clang_major__ < 16 and __APPLE__:
        # The below ranges example is still likely busted with the github actions runner's xcode apple clang 14

        sum = std.accumulate(args.cbegin() + 1, args.cend(), args[0], lambda(a, b, quote(unquote(a) + unquote(b))))
    else:
        sum: mut = args[0]
        for (arg in args|std.views.drop(1):
            sum = quote(unquote(sum) + unquote(arg))
        )
    ) : preprocessor

    return sum
)

def (main:
    std.cout << summation(1, 2, 3)
    c = "c"
    std.cout << summation("a"s, "b", c) << summation(5) << summation()
)
```

#### Optional arguments

Here's an example from the standard library macros located in the include directory. We use an optional match var for "specifier" to match virtual and otherwise decorated destructors as well as plain non-virtual destructors with a single macro pattern:

```python
# canonical empty destructor to default destructor:
# e.g.
# def (destruct:virtual:
#     pass
# )
# goes to
# def (destruct:virtual) = default
# For an empty non-default destructor
# use pass; pass
defmacro (def (destruct:specifier:
    pass
), specifier: Node|None:
    name: Node = quote(destruct)
    destructor = if (specifier:
        specified: Node = quote(unquote(name): unquote(specifier))
        specified
    else:
        name
    )
    return quote(def (unquote(destructor)) = default)
)
```

```python
# No "includes" needed to make use of the standard library macros

struct (Foo1:
    def (destruct:
        pass
        # pass  # uncomment for a non-default destructor
    )
)

struct (Foo2:
    # you may still write an explicitly default destructor if you must
    def (destruct:virtual) = default
)

class (Foo3:
    # non-None "specifier" match
    def (destruct:virtual:
        pass
    )
)

def (main:
    static_assert(not std.has_virtual_destructor_v<Foo1>)
    static_assert(std.has_virtual_destructor_v<Foo2>)
    static_assert(std.has_virtual_destructor_v<Foo3.class>)
)
```

### Kitchen Sink / mixing higher level and lower level ceto / external C++

Contrasting with the "Java style" / shared_ptr heavy visitor pattern shown above, the selfhost sources use a lower level version making use of C++ CRTP as well as the ```Foo.class``` syntax to access the underlying ```Foo``` in C++ (rather than ```shared_ptr<const Foo>```). This sidesteps the gotcha that ceto class instances aren't real "shared smart references" so **overriding** e.g. ```def (visit:override, node: BinOp)``` with ```def(visit: override, node: Add)``` is not possible because an **Add** (```std::shared_ptr<const Node>``` in C++) is not strictly speaking a derived class of ```std::shared_ptr<const BinOp>``` in C++. 

This code also demonstrates working with external C++ and more general/unsafe constructs like C++ iterators, raw pointers in combination with :unique classes, the C/C++ preprocessor, function pointers, and reinterpret_cast (and passing C++ types across dll boundaries, note: don't attempt to compile debug macro dlls without compiling a debug compiler first at least on Windows). This is an earlier version of the current selfhost/macro_expansion.cth:

```python

include <map>
include <unordered_map>
include <ranges>
include <functional>
include <span>

include (ast)
include (visitor)
include (range_utility)

if (_MSC_VER:
    include <windows.h>
    cpp'
    #define CETO_DLSYM GetProcAddress
    #define CETO_DLOPEN LoadLibraryA
    #define CETO_DLCLOSE FreeLibrary
    '
else:
    include <dlfcn.h>
    cpp'
    #define CETO_DLSYM dlsym
    #define CETO_DLOPEN(L) dlopen(L, RTLD_NOW)
    #define CETO_DLCLOSE dlclose
    '
) : preprocessor

struct (SemanticAnalysisError(std.runtime_error):
    pass
)

class (MacroDefinition:
    defmacro_node: Node
    pattern_node: Node
    parameters: std.map<string, Node>
    dll_path: std.string = {}
    impl_function_name: std.string = {}
)

class (MacroScope:
    parent: MacroScope.class:const:ptr = None

    macro_definitions: [MacroDefinition] = []

    def (add_definition: mut, defn: MacroDefinition:
        self.macro_definitions.push_back(defn)
    )

    def (enter_scope:
        s: mut = MacroScope()
        s.parent = this
        return s
    ) : MacroScope:mut
) : unique


def (macro_matches, node: Node, pattern: Node, params: const:std.map<std.string, Node>:ref:
    std.cout << "node: " << node.repr() << " pattern: " << pattern.repr() << "\n"

    # implementation ommitted see selfhost/macro_expansion.cth
    return {}
) : std.optional<std.map<std.string, Node>>


def (call_macro_impl, definition: MacroDefinition, match: const:std.map<std.string, Node>:ref:
    handle = CETO_DLOPEN(definition.dll_path.c_str())  # just leak it for now
    if (not handle:
        throw (std.runtime_error("Failed to open macro dll: " + definition.dll_path))
    )
    fptr = CETO_DLSYM(handle, definition.impl_function_name.c_str())
    if (not fptr:
        throw (std.runtime_error("Failed to find symbol " + definition.impl_function_name + " in dll " + definition.dll_path))
    )
    f = reinterpret_cast<decltype(+(lambda(m: const:std.map<std.string, Node>:ref, None): Node))>(fptr)  # no explicit function ptr syntax yet/ever(?)
    return (*f)(match)
) : Node


struct (MacroDefinitionVisitor(BaseVisitor<MacroDefinitionVisitor>):
    on_visit_definition: std.function<void(MacroDefinition, const:std.unordered_map<Node, Node>:ref)>

    current_scope: MacroScope:mut = None
    replacements: std.unordered_map<Node, Node> = {}

    def (expand: mut, node: Node:
        scope: mut:auto:const:ptr = (&self.current_scope)->get()
        while (scope:
            for (definition in ceto.util.reversed(scope->macro_definitions):
                match = macro_matches(node, definition.pattern_node, definition.parameters)
                if (match:
                    std.cout << "found match\n"
                    replacement = call_macro_impl(definition, match.value())
                    if (replacement and replacement != node:
                        std.cout << "found replacement for " << node.repr() << ": " << replacement.repr() << std.endl
                        self.replacements[node] = replacement
                        replacement.accept(*this)
                        return True
                    )
                )
            )
            scope = scope->parent
        )
        return False
    )

    def (visit: override:mut, node: Node.class:
        if (self.expand(ceto.shared_from(&node)):
            return
        )

        if (node.func:
            node.func.accept(*this)
        )

        for (arg in node.args:
            arg.accept(*this)
        )
    )

    def (visit: override:mut, call_node: Call.class:
        node = ceto.shared_from(&call_node)
        if (self.expand(node):
            return
        )

        node.func.accept(*this)

        for (arg in node.args:
            arg.accept(*this)
        )

        if (node.func.name() != "defmacro":
            return
        )

        if (node.args.size() < 2:
            throw (SemanticAnalysisError("bad defmacro args"))
        )

        pattern = node.args[0]

        if (not isinstance(node.args.back(), Block):
            throw (SemanticAnalysisError("last defmacro arg must be a Block"))
        )

        parameters: mut = std.map<std.string, Node>{}

        if (defined(__clang__) and __clang_major__ < 16:
            match_args = std.vector(node.args.cbegin() + 1, node.args.cend() - 1)
        else:
            match_args = std.span(node.args.cbegin() + 1, node.args.cend() - 1)
        ) : preprocessor

        for (arg in match_args:
            name = if (isinstance(arg, Identifier):
                arg.name().value()
            elif not isinstance(arg, TypeOp):
                throw (SemanticAnalysisError("bad defmacro param type"))
            elif not isinstance(arg.args[0], Identifier):
                throw (SemanticAnalysisError("bad typed defmacro param"))
            else:
                arg.args[0].name().value()
            )
            i = parameters.find(name)
            if (i != parameters.end():
                throw (SemanticAnalysisError("duplicate defmacro params"))
            )
            parameters.emplace(name, arg)
        )

        defn = MacroDefinition(node, pattern, parameters)
        self.current_scope.add_definition(defn)
        self.on_visit_definition(defn, self.replacements)
    )

    def (visit: override:mut, node: Module.class:
        s: mut = MacroScope()
        self.current_scope = s

        for (arg in node.args:
            arg.accept(*this)
        )
    )

    def (visit: override:mut, node: Block.class:
        outer: mut:MacroScope = std.move(self.current_scope)
        self.current_scope = outer.enter_scope()
        if (self.expand(ceto.shared_from(&node)):
            return
        )
        for (arg in node.args:
            arg.accept(*this)
        )
        self.current_scope = outer  # automatic move from last use
        # TODO: if outer is just 'mut' above we should still automatically std::move it? OTOH maybe not - keep need for an explicit type for something that is to be auto moved? Also, if you just write "outer2 = outer": Currently outer2 is a const auto definition created from std::moveing outer (creating a unique_ptr<non-const MacroScope>). I'm not so keen on making outer2 implicitly mut without a type annotation
    )
)

def (expand_macros, node: Module, on_visit: std.function<void(MacroDefinition, const:std.unordered_map<Node, Node>:ref)>:
    visitor: mut = MacroDefinitionVisitor(on_visit)
    node.accept(visitor)
    return visitor.replacements
) : std.unordered_map<Node, Node>
```
