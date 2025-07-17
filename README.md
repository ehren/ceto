## Intro

Ceto is an experimental language where calls may take indented blocks as arguments for a Python-inspired free-form but infix-friendly syntax extendable by ast macros. "Print should be a function" taken to its logical extreme. Classes have immutable safe reference semantics by default (const propagate_const shared_ptr to const by default) with ```.``` performing a safe maybe dereference even in generic code. Structs have value semantics but are passed by const ref by default. Performance compromises are acceptable to achieve memory safety with bounds checking by default, raw C++ references heavily restricted, and for loops reverting to checked indexing when a C++ range-based-for is not provably safe. Performance/safety escape hatches are available via unsafe blocks and external C++ though the intended language usecase is more pythonish glue-C++ than low level systems programming.

## Example

```python
include <ranges>

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
        reserve: Node = quote(util.maybe_reserve(unquote(result), unquote(zz)))
        reserve
    )

    return quote(lambda (:

        unquote(result): mut = []

        unquote(zz): mut:auto:ref:ref = unquote(z)
        unquote(pre_reserve_stmt)

        for (unquote(y) in unsafe(unquote(zz)):  # unsafe to use local var of ref type
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

namespace (util)

defmacro ([x, for (y in z)], x, y, z:
    # Use the existing 3-arg definition
    return quote([unquote(x), for (unquote(y) in unquote(z)), if (True)])
)

def (maybe_reserve<T>, vec: mut:[T]:ref, sized: mut:auto:ref:ref:
    # two mut:ref parameters requires unsafe to use
    unsafe(vec.reserve(std.size(std.forward<decltype(sized)>(sized))))
) : void:requires:requires(std.size(sized))

def (maybe_reserve<T>, vec: mut:[T]:ref, unsized: mut:auto:ref:ref:
    pass
) : void:requires:not requires(std.size(unsized))
```

```python
include <numeric>
include <future>
include <span>

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

class (UniqueFoo:
    consumed: [UniqueFoo] = []

    def (size:
        return self.consumed.size()
    )
    
    def (consuming_method: mut, u: UniqueFoo:
        Foo(42).method(u)  # "u" passed by const:ref
        self.consumed.append(u)  # "u" passed by value (cppfront inspired std.move on last use)
    )
) : unique

def (string_join, vec: [std.string], sep = ", "s:

    # std.string, std.vector and various other things passed by const:ref by default
    static_assert(std.is_same_v<decltype(vec), const:std.vector<std.string>:ref>)
    static_assert(std.is_same_v<decltype(sep), const:std.string:ref>)

    if (vec.empty():
        return ""
    )

    unsafe (:
        # 3 things require unsafe below:
        #   1) Direct use of C++ iterators.
        #   2) vec[0] is a reference - safe code must copy to a value before passing or 
        #      an elided static_assert that no aliasing related badness occurs though the 
        #      other parameters would fail. Note: vec[0] is still bounds checked (use 
        #      vec.unsafe[0] to avoid).
        #   3) lambda with ref capture is always unsafe - there is a safe (at least in 
        #      single threaded code) implicit capture mechanism shown below.
        return std.accumulate(vec.cbegin() + 1, vec.cend(), vec[0],
            lambda[&sep] (a, b, a + sep + b))
    )
): std.string

defmacro (s.join(v), s: StringLiteral, v:
    return quote(string_join(unquote(v), unquote(s)))
)

def (main, argc: int, argv: const:char:ptr:const:ptr:

    # macro invocations:
    args = [std.string(a), for (a in std.span(argv, argc))]
    summary = ", ".join(args)

    f = Foo(summary)  # implicit make_shared / extra CTAD:
                      # in C++ f is a const ceto::propagate_const<std::shared_ptr<const Foo<decltype(summary)>>>

    f.method(args)    # autoderef of f
    f.method(f)       # autoderef also in the body of 'method'
    calls_method(f)   # autoderef in the body of calls_method (and method)

    fut: mut = std.async(std.launch.async, lambda(:

        # Implicit copy capture (no capture list specified) for shared/weak
        # ceto-class instances, arithmetic types, and enums only.

        f.method(f).data_member
    ))

    std.cout << fut.get()

    u: mut = UniqueFoo()    # u is a "non-const" ceto::propagate_const<std::unique_ptr<"non-const" UniqueFoo>> in C++
    u2 = UniqueFoo()        # u2 is a non-const ceto::propagate_const<std::unique_ptr<const UniqueFoo>> in C++

    u.consuming_method(u2)  # implicit std.move from last use of u2.
                            # :unique are non-const (allowing move) but
                            # unique_ptr-to-const by default.

    u.consuming_method(u)   # in C++: CETO_AUTODEREF(u).consuming_method(std::move(u))
)
```

Note that ```:``` either marks the start of a ```Block``` or denotes a general purpose binary operator ([TypeOp in ast.cth](https://github.com/ehren/ceto/blob/main/selfhost/ast.cth)) available to the macro system but functioning as a type separator for C++ multiword types and specifiers; see [precedence table](https://github.com/ehren/ceto/blob/main/ceto/parser.py#L161). See [include/convenience.cth](https://github.com/ehren/ceto/blob/main/include/convenience.cth) for a built-in macro making creative use of ```TypeOp``` for a Python/JSON like std.map initialization syntax:

```python
class (Foo:
    x
)

def (main:
    # map: std.map = { "1": 1, "2": 2.0}  # error (key-val types must match)
    map: std.unordered_map = { 1: [Foo(1), Foo(2)], 2: [Foo(3)]}
    for ((key, vec) in map:
        # A range-based C++ for loop is emitted here because map is a value.
        # Were it a reference (or if a reference to it escapes) a static_assert
        # that std.size checked indexing iteration is not available would fire.
        # Use unsafe_for to unconditionally emit a C++ range-based-for.
        std.cout << key << std.endl
        for (foo in vec:
            std.cout << foo.x
        )
    )
)
```

On the topic of ```:```, how do we support ```map[key]``` when key is an ```int``` without running afoul of our bounds checked container access? (main bounds checking logic has been stolen crudely from cppfront; see the macros at [include/boundscheck.cth](https://github.com/ehren/ceto/blob/main/include/boundscheck.cth)) We have a ```concept``` to special case map specifically:

```python
is_map_type: template<class:T>:concept = std.same_as<typename:T.value_type, std.pair<const:typename:T.key_type, typename:T.mapped_type>>
```

## Usage

```bash
$ git clone https://github.com/ehren/ceto.git
$ cd ceto
$ pip install .
$ ceto ./tests/example.ctp
```

## Safety Note

We're working on an additional construct: ```unsafe(external_cpp=[std.async, std.span, std.accumulate, printf])``` (together with simple name mangling to avoid unexpected function overloading of external C++). Until that is implemented, one must be very careful with including external C++ header files. 

Example:

```python
include (some_ceto_module)  # safe (assuming some_ceto_module.cth is safe)
include <future>  # wildly unsafe
include <thread>  # even moreso
include <span>  # ditto
include"some_random_header.h"  # ditto
```

There is no current support for c++20 modules. Ceto modules are independently parsed however allowing some module-like features to not pollute downstream includers. Examples:

- ```unsafe()``` call at the beginning of a file marks all functions/code unsafe in that file only
- ```namespace (util.detail)``` means all code that follows is in that namespace avoiding the extra indent of the ```Block``` form (flat is better than nested).
- ```unsafe(external_cpp=[...])``` affects either the file or a local scope but not including files.

The generated C++ code uses header inclusion. Perhaps there is a chance to implement ```import(blah)``` together with C++ modules in the future.

Memory safety even in pure ceto code is a work in progress (see the memory safety roadmap here) but even a single ```unsafe``` invites the spectre of C++ undefined behavior:

```python
include <ranges>

struct (Foo:
    vec: [int]

    def (foo: mut, x:
        # x, lacking a type annotation, is implicitly const:auto:ref
        static_assert(std.is_reference_v<decltype(x)> and std.is_const_v<std.remove_reference_t<decltype(x)>>)

        # this should cause a vector relocation, invalidating references:
        for (i in std.ranges.iota_view(0, std.ssize(self.vec) * 2):
            self.vec.append(i)
        )

        # hopefully this ref is still valid (not if you evade checks with unsafe!)
        std.cout << x << std.endl  
    )

    def (good: mut:
        # self.foo(vec[0])  # static_assert failure
        val = self.vec[0]
        self.foo(val)
    )

    def (bad: mut:
        self.foo(unsafe(self.vec[0]))  # UB

        r: mut:auto:ref = self.vec[0]
        self.foo(unsafe(r))  # why local ref vars are unsafe (UB)
    )
)

def (main:
    f: mut = Foo([1, 2, 3, 4])
    f.good()  # prints 1
    f.bad()   # UB (and reliably prints garbage x2)
)
```

## Language Tour

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

This project uses many of the ideas from the https://github.com/lukasmartinelli/py14 project such as the implicit insertion of *auto* (though in ceto it's implict *const auto* for untyped locals and *const auto&* for untyped params). The very notion of generic python functions as C++ template functions is also largely the same.

We've also derived our code generation of Python like lists as ```std.vector``` from the project.

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

Though, we require a *mut* annotation and rely on *std.ranges*, the wacky forward inference via *decltype* to codegen the type of results above as ```std::vector<decltype(fun(std::declval<std::ranges::range_value_t<decltype(values)>>()))>``` derives from the py14 implementation.

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

    for ((x, y) in tuples:  # const auto
        std.cout << x << y << "\n"
    )

    for ((x, y):mut:auto:ref in tuples:  # auto&
        unsafe(:
            # a local var of ref type is unsafe
            x += 1
            y += 2
        )
    )

    for ((x, y):mut in tuples:  # just auto
        static_assert(std.is_same_v<decltype(x), int>)
        static_assert(std.is_same_v<decltype(y), int>)
    )
)
```

### Shared / weak / thread

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
        unsafe(visitor.visit(*this))
    )

    def (clone: override:
        c: mut = Module(self.cloned_args(), self.source)
        return c
    ) : Node:mut
)
```

This ```accept``` has better runtime perforance than ```SimpleVisitor```'s class heavy version above but 
note that raw pointer dereference e.g. ```*this``` and mutable C++ references in methods (allowing bad aliasing through ```this```) requires ```unsafe```.

### struct

"The struct is a class notion is what has stopped C++ from drifting into becoming a much higher level language with a disconnected low-level subset." - Bjarne Stroustrup

```python
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
    # Note that for the class case - Foo is passed by const ref (to shared_ptr), Foo:mut is passed by value (because of propagate_const)
    static_assert(std.is_same_v<decltype(f), const:Foo>)
    static_assert(not std.is_reference_v<decltype(f)>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(f)>>)
    std.cout << f.x
)

def (by_mut_ref, f: Foo:ref:mut:  # pass by non-const reference (mut:Foo:ref also fine - west mut)
    static_assert(std.is_same_v<decltype(f), Foo:ref>)
    static_assert(std.is_reference_v<decltype(f)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(f)>>)
    # no unsafe block needed for a single mut:ref param 
    f.x += "hi"
    std.cout << f.x
)

# TODO: Note that using fully notated const pointers like below is recommended for all ceto code. 
# The const by default (unless :unique) for function parameters feature behaves a bit like add_const_t currently
# (the multiple mut syntax "mut:Foo:ptr:mut" is not even currently supported for Foo** in C++ -
#  while mut:Foo:ptr or Foo:ptr:mut works currently, future ceto versions may require additional mut/const annotations)
def (by_ptr, f: const:Foo:ptr:const:
    static_assert(std.is_same_v<decltype(f), const:Foo:ptr:const>)
    std.cout << unsafe(f->x)  # no autoderef for raw pointers; no explicit deref (non-null checked) in safe-mode
)

def (main:
    f = Foo("blah")
    by_const_ref(f)
    by_val(f)
    by_const_val(f)
    # by_mut_ref(f)  # error: binding reference of type ‘Foo&’ to ‘const Foo’ discards qualifiers
    fm : mut = f  # copy
    by_mut_ref(fm)
    by_ptr(unsafe(&f))
)
```




### Macros

Macros should be used sparingly for extending the language. When possible, C++ templates or preprocessor macros should be preferred.

Macros are unhygienic (use gensym for locals to avoid horrific capture bugs). Automatic hygiene at least for simple local variables as well as automatic unquoting of params might be implemented in the future (more pressingly we'll need checks to prevent expansion of paramater derived nodes in unsafe blocks generated by the macro - similar to the rust clippy macro_metavars_in_unsafe)

```python
include <ranges>
include <algorithm>

namespace (myproj.util:

    # long form template function syntax - short form "def(foo<T>" is itself a macro but
    # doesn't support complicated nested typenames nor ...
    # Syntactically ... is either a postfix operator or an Identifier (not a binary operator):

    def (python_like_range: template<typename:...:Args>, args: mut:Args:ref:ref:...:
        if ((sizeof...)(Args) == 1:
            zero: std.remove_cvref_t<typename:std.tuple_element<0, std.tuple<Args...>>::type> = 0
            return std.ranges.iota_view(zero, std.forward<Args>(args)...)
        else:
            return std.ranges.iota_view(std.forward<Args>(args)...)
        ) : constexpr
    ) : decltype(auto)

    # std.ranges.contains can be used in c++23 but we'll implement our own:
    def (contains, container, element: const:typename:std.remove_reference_t<decltype(container)>::value_type:ref:
        return unsafe(std.find(container.cbegin(), container.cend(), element) != container.cend())
    )
)

defmacro(a in b, a, b:
    if ((call = asinstance(a.parent().parent(), Call)):
        name = call.func.name()
        if (name and myproj.util.contains(["for"s, "unsafe_for"s], name.value()):
            # don't rewrite the "in" of a for-in loop (pitfall of a general syntax!)
            return None
        )
    )

    return quote(myproj.util.contains(unquote(b), unquote(a)))
)

def (main:
    for (x in myproj.util.python_like_range(10):
        if (x in [2, 4, 6]:
            std.cout << x
        )
    )
)
```

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

defmacro (summation(args), args: [Node]:
    if (not args.size():
        return quote(0)
    )

    if (defined(__clang__) and __clang_major__ < 16 and __APPLE__:
        accumulator = lambda(a, b, quote(unquote(a) + unquote(b))
        unsafe (:
            return std.accumulate(args.cbegin() + 1, args.cend(), args[0], accumulator)
        )
    else:
        sum: mut = args[0]
        for (arg in args|std.views.drop(1):
            sum = quote(unquote(sum) + unquote(arg))
        )
        return sum
    ) : preprocessor
)

def (main:
    std.cout << summation(1, 2, 3)
    c = "c"
    std.cout << summation("a"s, "b", c) << summation(5) << summation()
)
```

#### Optional arguments

Here are two examples from the standard library macros located in the include directory. In the first we use an optional match var for "specifier" to match virtual and otherwise decorated destructors as well as plain non-virtual destructors with a single macro pattern. In the second we allow an abbreviated syntax for function template defs that supports optional function decorators (like "static").

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

# def (foo<T> -> def (foo:template<typename:T>
defmacro(def (func_name<T>:specifier, args), func_name, T: Identifier, specifier: Node|None, args: [Node]:
    template_header: Node = quote(template<typename:unquote(T)>)
    specified_template = if (specifier:
        specified: Node = quote(unquote(template_header):unquote(specifier))
        specified
    else:
        template_header
    )
    new_args: mut:[Node] = [quote(unquote(func_name):unquote(specified_template))]
    unsafe (:
        new_args.insert(new_args.end(), args.begin(), args.end())
    )
    return Call(quote(def), new_args)
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
    # You may still write an explicitly default destructor if you must
    def (destruct:virtual) = default

    # Abbreviated explicit template function syntax
    def (func<T>:static, x: T:
        std.cout << x
    )
)

class (Foo3:
    # non-None "specifier" match
    def (destruct:virtual:
        pass
    )
)

def (func<T>, x: T:
    std.cout << x
)

def (main:
    static_assert(not std.has_virtual_destructor_v<Foo1>)
    static_assert(std.has_virtual_destructor_v<Foo2>)
    static_assert(std.has_virtual_destructor_v<Foo3.class>)
    Foo2.func(1)
    func<std.string>("1")
)
```

### std.optional / autoderef details

```python
def (main:
    optional_map: std.optional<std.map<std.string, int>> = std.map<std.string, int> {
        {"zero", 0}, {"one", 1}}

    optional_str: std.optional<std.string> = std.nullopt

    if (optional_map:
        std.cout << optional_map.at("zero")  # autoderef
    )

    if (optional_str:
        std.cout << optional_str.size()   # autoderef
        std.cout << optional_str  # error: no autoderef without operator(".")
        std.cout << optional_str.value()
    )

    # we have the billion dollar mistake like Python just no null-derefence UB
    # - better than a billion?.question?.marks??
    # optional_str.length()  # std.terminate()
)
```

As shown above no deref takes place when calling a method of ```std.optional```. That is, to call a method `value()` on the underlying value rather than the optional call `.value().value()`.

(this example also illustrates that for ceto classes and structs round parenthesese must be used e.g.  ```Foo(x, y)``` even though the generated code makes use of curlies e.g. ```Foo{x, y}``` (to avoid narrowing conversions). For external C++ round means round - curly means curly (```std.vector<int>(50, 50)``` is a 50 element vector of 50)

Note that to call the smart ptr `get` method (rather than a `get` method on the autoderefed instance) use ```unsafe((&obj)->get())``` or ```unsafe(std.addressof(obj)->get())```.

In addition, while we don't support deref without ```.``` one can add it implicitly in certain situations (note ```override``` caveats mentioned below when over-relying on smart pointers):

```python
class (Foo:

    def (operator("+"), foo:Foo:
        std.cout << "adding foo and foo (in the member function)\n"
        return self
    )

    def (operator("+"), other:
        std.cout << "adding foo and other (in the member function)\n"
        return self
    )
)

# autoderef occurs because f.operator("+") uses '.'

def (operator("+"), f:Foo, x:
    return f.operator("+")(x)
)

def (operator("+"), x, f:Foo:
    return f.operator("+")(x)
)

def (operator("+"), x:Foo, f:Foo:
    return f.operator("+")(x)
)

def (main:
    Foo() + 1
    1 + Foo()
    two_foo = Foo() + Foo()
    (1 + two_foo + 1) + Foo()
)
```

### Kitchen Sink / mixing higher level and lower level ceto / external C++

Contrasting with the "Java style" / shared_ptr heavy visitor pattern shown above, the selfhost sources use a lower level version making use of C++ CRTP as well as the ```Foo.class``` syntax to access the underlying ```Foo``` in C++ (rather than ```shared_ptr<const Foo>```). This sidesteps the gotcha that ceto class instances aren't real "shared smart references" so **overriding** e.g. ```def (visit:override, node: BinOp)``` with ```def(visit: override, node: Add)``` is not possible because an **Add** (```std::shared_ptr<const Node>``` in C++) is not strictly speaking a derived class of ```std::shared_ptr<const BinOp>``` in C++. 

This code also demonstrates working with external C++ and more general/unsafe constructs like C++ iterators, raw pointers in combination with :unique classes, the C/C++ preprocessor, function pointers, and reinterpret_cast (and passing C++ types across dll boundaries, note: don't attempt to compile debug macro dlls without compiling a debug compiler first at least on Windows). This is an earlier version of the current selfhost/macro_expansion.cth:

```python
unsafe()

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
        outer: mut:MacroScope = std.move(self.current_scope)  # TODO because of the 'kill' for self.current_scope on the next line could we automatically insert the move here?
        self.current_scope = outer.enter_scope()
        if (self.expand(ceto.shared_from(&node)):
            return
        )
        for (arg in node.args:
            arg.accept(*this)
        )
        self.current_scope = outer  # automatic move from last use
    )
)

def (expand_macros, node: Module, on_visit: std.function<void(MacroDefinition, const:std.unordered_map<Node, Node>:ref)>:
    visitor: mut = MacroDefinitionVisitor(on_visit)
    node.accept(visitor)
    return visitor.replacements
) : std.unordered_map<Node, Node>
```
