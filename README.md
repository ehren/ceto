## Intro

Ceto is an experimental language where calls may take indented blocks as arguments for a Python-inspired free-form but infix-friendly syntax extendable by ast macros. The semantics should feel a bit like Swift (classes are reference counted; structs are value types) or even an immutable by default Python with support for many native C++ constructs and external C++. We're also taking a stab at C++ safety with unsafe blocks/unsafe.extern declarations, bounds checking, safe usages of raw C++ references relegated to function parameters with aliasing/invalidation prevention static_asserts added at the call site, and for-loops that revert to size checked-indexing for (references to) contiguous owning containers when a raw C++ range-based-for is not provably safe. Class instances are propagate_const shared_ptr to const by default encouraging immutability (with all mutation marked by `mut`).

## Example

Any expression can be redefined via the macro system. That's used here to provide python-style optional keyword arguments to a toy print function macro:

```python
include <fstream>

defmacro (print(args, stream_arg), args:[Node], stream_arg: Assign|None:

    decorate_error: mut = False

    stream = if (stream_arg:
        if (stream_arg.equals(quote(file = std.cerr)):
            decorate_error = True
            quote(std.cerr)
        elif stream_arg.args[0].equals(quote(file)):
            rhs = stream_arg.args[1]
            if (isinstance(rhs, StringLiteral):
                # we'll be nice and open a file in append mode for you
                quote(std.ofstream(unquote(rhs), std.ios.app))
            else:
                rhs
            )
        else:
            throw (std.invalid_argument('unexpected "keyword argument": ' + stream_arg.repr()))
        )
    else:
        quote(std.cout)
    )

    result: mut = stream

    if (decorate_error:
        result = quote(unquote(result) << "🙀")
    )

    unsafe.extern(std.views.take)

    for (arg in args | std.views.take(std.ssize(args) - 1):
        result = quote(unquote(result) << unquote(arg))
    )

    # add a newline but try to avoid a double newline
    last = if (args.size():
        back = args.back()
        if (back.equals(quote(std.endl)) or (isinstance(back, StringLiteral)
                                             and back.str.ends_with("\n")):
            back
        else:
            quote(unquote(back) << std.endl)
        )
    else:
        quote(std.endl)
    )

    return quote(unquote(result) << unquote(last))
)

def (main:
    unsafe.extern(std.ofstream)
    x: mut = []
    x.append(5)
    print(x[0], file=std.ofstream("example.txt", std.ios.app))
)
```

As well as defining a macro this code makes two uses of defmacro standard library built-ins. `x[0]` expands to a bounds-check call via the macro system (with the C++ compile time bounds checking logic derived from Herb Sutter's cppfront though bugs are our own; see [include/boundscheck.cth](https://github.com/ehren/ceto/blob/main/include/boundscheck.cth)). While

```python
isinstance(back, StringLiteral) and back.str.ends_with("\n")
```

is expanded via a built-in defmacro in [include/convenience.cth](https://github.com/ehren/ceto/blob/main/include/convenience.cth) to something like:

```python
lambda (:
    new_back = asinstance(back, StringLiteral)  # dynamic_pointer_cast convenience
    return new_back != None and new_back.str.ends_with("\n")
) ()
```

## Usage

```bash
$ git clone https://github.com/ehren/ceto.git
$ cd ceto
$ pip install .
$ ceto ./tests/example.ctp
```

## Language Tour

### Simple Listcomp

We can use the existing list literal and call syntax with the macro system for a python-ish list comprehension:

```python
defmacro ([x, for (y in z), if (c)], x, y, z, c:
    result = gensym()

    return quote(lambda (:
        unquote(result): mut = []

        for (unquote(y) in unquote(z):
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

def (main:
    vec = [x*2, for (x in std.ranges.iota_view(0, 10))]

    for (i in vec:
        std.cout << i
    )
)
```

### Pre-reserving listcomp (ceto macros + ordinary C++ template metaprogramming)

The above simple listcomp macro works but we can improve it by pre-reserving the size of our results vector when the max size of the listcomp result is known:

```python
defmacro ([expr, for (i in iterable), if (cond)], expr, i, iterable, cond:
    result = gensym()
    iterable_param = gensym()

    pre_reserve_stmt = if (isinstance(cond, EqualsCompareOp) and std.ranges.any_of(
                           cond.args, lambda(a, a.equals(expr) or a.equals(i))):
        # Don't bother pre-reserving a std.size(z) sized vector for simple searches 
        # e.g. [x, for (y in z) if (y == something)]
        dont_reserve: Node = quote(pass)
        dont_reserve
    else:
        reserve: Node = quote(maybe_reserve(unquote(result), unquote(iterable_param)))
        reserve
    )

    return quote(lambda (unquote(iterable_param): mut:auto:ref:ref:
        unquote(result): mut = []
        unquote(pre_reserve_stmt)

        for (unquote(i) in unquote(iterable_param):
            unquote(if (cond.name() == "True":
                # Omit literal if (True) check (reduce clutter for 2-arg case below)
                quote(unquote(result).append(unquote(expr)))
            else:
                quote(if (unquote(cond):
                    unquote(result).append(unquote(expr))
                ))
            ))
        )

        unquote(result)
    ) (unquote(iterable)))
)

defmacro ([expr, for (i in iterable)], expr, i, iterable:
    # Use the existing 3-arg definition
    return quote([unquote(expr), for (unquote(i) in unquote(iterable)), if (True)])
)

def (maybe_reserve<T>, vec: mut:[T]:ref, sized: mut:auto:ref:ref:
    unsafe.extern(std.forward)
    vec.reserve(std.size(std.forward<decltype(sized)>(sized)))
) : void:requires:requires(std.size(sized))

def (maybe_reserve<T>, vec: mut:[T]:ref, unsized: mut:auto:ref:ref:
    pass
) : void:requires:not requires(std.size(unsized))

def (main:
    l = [x, for (x in std.ranges.iota_view(0, 10)), if (x % 2 == 0)]

    l2 = [x + 1, for (x in l)]
 
    for (i in [x, for (x in l2), if (x > 5)]:
        std.cout << i
    )
 
    for (i in [x * 100, for (x in l)]:
        std.cout << i
    )

    unsafe.extern(std.views.filter)

    filtered_view: mut = [0, 1, 2, 3] | std.views.filter(lambda(x, x < 5))

    # no std.size available for pre-reserve case:
    filtered_via_listcomp = [x, for (x in filtered_view), if (x < 42)]

    for (x in filtered_via_listcomp:
        std.cout << x
    )

    # in practice this is a better option for converting a view to a vec:

    if (__cplusplus >= 202302L:
        filtered_vec = filtered_view | std.ranges.to<std.vector>()
        for (x in filtered_vec:
            std.cout << x
        )
    ): preprocessor

    # even better: c++20 polyfill for std.ranges.to<std.vector>() via builtin macro
    filtered_via_polyfill = filtered_view | []

    static_assert(std.is_same_v<decltype(filtered_via_polyfill), const:std.vector<int>>)
)
```

A version of the listcomp macro is provided by default as a standard library built-in, see [include/listcomp.cth](https://github.com/ehren/ceto/blob/main/include/listcomp.cth) 

### Parameter passing, ```class``` basics

You can get somewhat far with python 2 like non-type annotated code as a shorthand for unconstrained C++ template metaprogramming and duck typing.

```python
include <numeric>
include <future>
include <span>

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

def (calls_method, obj, arg:
    return obj.method(arg)
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
        return std.accumulate(vec.cbegin() + 1, vec.cend(), vec[0],
            lambda[&sep] (a, b, a + sep + b))
    )
): std.string

defmacro (s.join(v), s: StringLiteral, v:
    return quote(string_join(unquote(v), unquote(s)))
)

def (main, argc: int, argv: char:pointer:pointer:
    unsafe.extern(std.span, std.async)

    # macro invocations:
    args = [std.string(a), for (a in std.span(unsafe(argv), argc))]
    summary = ", ".join(args)

    f = Foo(summary)  # implicit make_shared / extra CTAD:
                      # in C++ f is a const ceto::propagate_const<std::shared_ptr<const Foo<decltype(summary)>>>

    f.method(args)    # autoderef of f
    f.method(f)       # autoderef also in the body of 'method'
    calls_method(f, f)   # autoderef in the body of calls_method (and method)

    # copy capture (no capture list specified) for shared/weak instances,
    # arithmetic types, and enums only:
    fut: mut = std.async(std.launch.async, lambda(f.method(f)))
    fut.get().method(f)

    u: mut = UniqueFoo()
    u2 = UniqueFoo()

    u.consuming_method(u2)  # implicit std.move from last use of u2.
                            # :unique are non-const (allowing move) but
                            # unique_ptr-to-const by default.

    u.consuming_method(u)   # in C++: CETO_AUTODEREF(u).consuming_method(std::move(u))
)
```

Duck typed functions are even slightly more generic than unconstrained C++ templates because `.` is a maybe autoderef when not an implicit scope resolution. This works by compiling a generic / non-type-annotated function like

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

where `ceto::mad` (maybe allow dereference) amounts to just `f` (allowing the dereference via `*` to proceed) when `f` is a smart pointer or optional, otherwise returning the `std::addressof` of `f` to cancel the dereference for anything else (more or less equivalent to ordinary attribute access `f.foo()` in C++). This is adapted from this answer: https://stackoverflow.com/questions/14466620/c-template-specialization-calling-methods-on-types-that-could-be-pointers-or/14466705#14466705 except the ceto implementation (see include/ceto.h) avoids raw pointer autoderef (you may still use `*` and `->` when working with raw pointers). When `ceto::mad` allows a dereference, it also performs a terminating nullptr check (use `->` for an unchecked access in ```unsafe``` contexts).

### Safety Status

100% safe* ceto programs, free of the ```unsafe``` keyword, should operate on the maxim that if something can't safely be passed by ref it should be copied. If it's expensive to copy, wrap it in a class to refcount it. When copies occur is as in C++ (aided by "always (const) auto" for python-style unannotated variable declarations). When something is (implicitly) passed by raw C++ reference is also as in C++ (no call-side borrow syntax required). Cases of potential memory unsafety when passing a ref due to aliasing/invalidation through the other arguments are stopped at the call site via hidden static_asserts. Evading these checks with the keyword ```unsafe``` can lead to wild non-local propagation of memory unsafety as in the method ```bad``` below:

```python
# Example Output: 1
# Example Output: -529464832
# Example Output: -488570880
# Example Output: -520011712
# Example Output: -520011712
# Example Output: 11

struct (HoldsRef:
    x: int:ref
)

struct (Foo:
    vec: [int]

    def (foo: mut, x:
        # x, lacking a type annotation, is implicitly const:auto:ref
        static_assert(std.is_reference_v<decltype(x)> and std.is_const_v<std.remove_reference_t<decltype(x)>>)

        # this could cause a vector relocation, invalidating references:
        for (i in std.ranges.iota_view(0, std.ssize(self.vec)):
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
        self.foo(unsafe(r))  # local ref vars are almost always unsafe (UB)

        unsafe.extern(std.ref)
        
        self.foo(std.ref(self.vec[0]))  # UB
        self.foo(std.ref(unsafe(r)))  # UB

        # std.ref (like other unsafe.extern views and spans) is itself very dangerous
        std.cout << lambda(:
            x = 5
            return std.ref(x)
        ) ().get()  # UB

        # as are classes and structs that hold raw C++ references
        std.cout << lambda(:
            x: mut = 5
            # ceto defined classes/structs holding raw C++ refs can only be created in an unsafe context
            return unsafe(HoldsRef(x))
        ) ().x  # UB
    )
)

def (main:
    f: mut = Foo([1, 2, 3, 4])
    f.good()  # prints 1
    f.bad()   # UB (and reliably prints garbage)
)
```

See [tests/regression/errors/bad_alias.ctp](https://github.com/ehren/ceto/blob/main/tests/regression/errors/bad_alias.ctp) for more reference passing assert examples (e.g. you may pass by ref to a 1 argument callable - but not if it's a non-stateless lambda). Note that accessing global variables requires a python-ish ```g: global``` declaration (only permitted in unsafe contexts).

## Further Reading / Lang Reference

### More generic functions, python-like list/vector notation

This project was originally based on the py14 codebase of Lukas Martinelli.

Among other things the code generation of Python like lists as ```std.vector``` derives from that project.

Here's a similar example to [the py14 README](https://github.com/lukasmartinelli/py14?tab=readme-ov-file#how-it-works):

```python
# Test Output: 123424681234123412341234

def (map, values, fun:
    results: mut = []
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
    map(l, foo_generic<int>)
    map(l, lambda (x:int, foo_generic(x)))
    map(l, lambda (x, foo_generic(x)))  # acceptable though clang 14 -O3 produces worse code than passing foo_generic<int> directly. 
)
```

Though, we require a `mut` annotation and rely on `std.ranges`, the wacky forward inference via `decltype` to codegen the type of results above as ```std::vector<decltype(fun(std::declval<std::ranges::range_value_t<decltype(values)>>()))>``` derives from the py14 implementation.

### Classes, Inheritance, init

Class definitions are intended to resemble Python dataclasses

```python
# Test Output: 5555.0one

include <map>
include <string>

class (Generic:
    x  # 1-arg constructor, deleted 0-arg constructor
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

All constructors whether implicit or defined by an init method use the C++ keyword ```explicit```

### Tuples, "tuple unpacking" (std.tuple / structured bindings / std.tie)

```python
def (foo, tuple1: (int, int), tuple2 = (0, 1):
    # TODO perhaps Python like tuple1[0] notation for transpiler known tuples
    return (std.get<0>(tuple1), std.get<1>(tuple2))
)

def (main:
    tuples: mut = []

    for (i in std.ranges.iota_view(0, 10):
        tuples.append((i, i + 1))
    )

    # declaration (C++ structured binding)
    (a, b) = (tuples[0], tuples[1])
    tuples.append(a)

    # reassignment (std::tie)
    (tuples[4], tuples[6]) = ((0, 0), b)

    (std.get<0>(tuples[7]), std.get<1>(tuples[7])) = foo(tuples[7])

    for ((x, y) in tuples:
        std.cout << x << y << "\n"
    )

    for ((x, y):mut:auto:ref in tuples:
        unsafe(:
            x += 1
            y += 2
        )
    )

    for ((x, y):mut in tuples:
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

You can write the Visitor just like Java* (with caveats). This example demonstrates non-trivial use of self and mutable ceto-class instances

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

### propagate_const by default

```python
class (Foo:
    x: int

    def (foo:
        std.cout << "i'm const\n"
    )

    def (foo: mut:
        self.x += self.x
        std.cout << "i'm mut\n"
    )
)

def (calls_foo, f:
    f.foo()  # i'm const (even if handed a mut) thanks to propagate_cost
)

def (calls_foo_through_mut, m: mut:
    m.foo()  # const or mut according to whether m is a Foo or a Foo:mut
)

def (calls_foo_through_mut_copy, f:
    m: mut = f
    m.foo()  # const or mut according to whether m is a Foo or a Foo:mut
)

def (main:
    m: mut = Foo(1)
    c = Foo(2)

    c.foo()  # i'm const
    m.foo()  # i'm mut

    calls_foo(c)  # i'm const
    calls_foo(m)  # i'm const (thanks to propagate_const)

    calls_foo_through_mut(c)  # i'm const
    calls_foo_through_mut_copy(c)  # i'm const

    calls_foo_through_mut(m)  # i'm mut
    calls_foo_through_mut_copy(m)  # i'm mut

    const_vec_of_mut: [Foo:mut] = [m]
    const_vec_of_mut[0].foo()  # i'm const (thanks to propagate_const)

    vec_mut_copy: mut = const_vec_of_mut
    vec_mut_copy[0].foo()  # i'm mut (it was mut (that is Foo:mut) to begin with - and now the instance we're calling it through is mut too)

    mut_vec_of_const: mut:[Foo] = [c, m]
    mut_vec_of_const[0].foo()  # i'm const
    mut_vec_of_const[1].foo()  # i'm const (conversion of m to Foo aka Foo:const during creation of mut_vec_of_const)
    mut_vec_of_const = []      # the elements are (ptr to) const but the vec itself is mutable
)
```

If we were using merely ```std::shared_ptr<Foo>``` for class instance variables rather than ```ceto::propagate_const<std::shared_ptr<Foo>>``` the above lines "i'm const (thanks to propage_const)" would instead read "i'm mut (no thanks to shared_ptr)"

In fact, without propagate_const our code would behave very much like swift:

```swift
class Details {
    var id: Int = 0
}

class Person {
    var details: Details
    init(details: Details) { self.details = details }
}

let details = Details()
details.id = 5  // Allowed, 'id' is a var property even though the instance is created with let
let person = Person(details: Details())
person.details = details // Allowed, property is var even though instance created with let
person.details.id = -1 // Allowed, 'details' and 'id' are var properties
print(person.details.id)  // -1
```

Where the equivalent ceto always requires a mut at the mutation site:

```python
# no mut annotation necessary/allowed for simple types (const may be used for const data members in C++ - though these are rarely a good idea)
class (Details:
    id: int = 0
)

# mut annotation needed for class instances if we want modifyable details
class (Person:
    details: Details:mut
)

def (main:
    details = Details()
    # details.id = 5  # error (details is a const var holding a Details:const aka Details)
    static_assert(std.is_const_v<decltype(details)> and std.is_same_v<std.remove_const_t<decltype(details)>, Details> and std.is_same_v<Details, Details:const>)

    # person = Person(details)    # error (Person expects Details:mut)
    mut_details: mut = Details()  # create a mut variable holding a Details:mut
    mut_details.id = 5  # ok

    person = Person(mut_details)
    # person.details = mut_details  # error (unlike swift if the instance is const then no modifications may occur even if the data member holds a mut)
    # person.details.id = -1        # error (same reason)

    mut_details.id = -1  # we can still modify through a mut instance var pointing to a mut
    std.cout << person.details.id  # -1

    mut_instance_of_const: mut = details  # while a mut binding holding a non-mut permits no direct mutation:
    # mut_instance_of_const.id = 5        # error
    mut_instance_of_const = None          # we may only reassign it
)
```

While we still have to to worry about the complications of mutable reference semantics we at least have that any function not containing 'mut' (and which transitively calls no other code with 'mut' or 'unsafe') can be assured to never modify a ceto class data member (important for future optimization and safety-check relaxation). 

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
    f.x += "hi"
    std.cout << f.x
)

# TODO: using fully notated const pointers like below is recommended for all ceto code. 
# The const by default (unless :unique) for function parameters feature behaves a bit like add_const_t currently
# (the multiple mut syntax "mut:Foo:pointer:mut" is not even currently supported for Foo** in C++ -
#  while mut:Foo:pointer or Foo:pointer:mut works currently, future ceto versions may require additional mut/const annotations)
def (by_pointer, f: const:Foo:pointer:const:
    static_assert(std.is_same_v<decltype(f), const:Foo:pointer:const>)
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
    by_pointer(unsafe(&f))
)
```

### Macros

Macros should be used sparingly for extending the language. When possible, C++ templates or preprocessor macros should be preferred.

Macros are unhygienic (use gensym for locals to avoid horrific capture bugs). Automatic hygiene at least for simple local variables as well as automatic unquoting of params might be implemented in the future (more pressingly we'll need checks to prevent expansion of paramater derived nodes in unsafe blocks generated by the macro - similar to the rust clippy macro_metavars_in_unsafe)

```python
include <algorithm>

namespace (myproj.util:

    # long form template function syntax - short form "def(foo<T>" is itself a macro but
    # doesn't support complicated nested typenames nor ...
    # Syntactically ... is either a postfix operator or an Identifier (not a binary operator):

    def (python_like_range: template<typename:...:Args>,
                      args: mut:Args:ref:ref:...:
        unsafe.extern(std.forward)
        if ((sizeof...)(Args) == 1:
            return std.ranges.iota_view(0, std.forward<Args>(args)...)
        else:
            return std.ranges.iota_view(std.forward<Args>(args)...)
        ) : constexpr
    ) : decltype(auto)

    # std.ranges.contains can be used in c++23 but we'll implement our own:
    def (contains, container,
                     element: const:typename:std.remove_reference_t<decltype(container)>::value_type:ref:
        return unsafe(std.find(container.cbegin(), container.cend(), element) != container.cend())
    )
)

defmacro(a in b, a, b:
    if ((call = asinstance(a.parent().parent(), Call)):
        if (call.func.name() == "for":
            # don't rewrite the "in" of a for-in loop (pitfall of a general syntax!)
            return None
        )
    )
    return quote(myproj.util.contains(unquote(b), unquote(a)))
)

def (main:
    unsafe.extern(printf)

    for (x in myproj.util.python_like_range(10):
        if (x in [2, 4, 6]:
            printf("%d", x)
        )
    )
)
```

#### Syntax Note

```:``` either marks the start of a ```Block``` or denotes a general purpose binary operator ([TypeOp in ast.cth](https://github.com/ehren/ceto/blob/main/selfhost/ast.cth)) available to the macro system but functioning as a type separator for C++ multiword types and specifiers; see [precedence table](https://github.com/ehren/ceto/blob/main/ceto/parser.py#L161). Here's a macro using ```TypeOp``` for a Python/JSON like ```std.map``` initialization syntax:

```python
defmacro(map_var: west:std.map:east = {keyvals}, keyvals: [TypeOp],
         map_var: Identifier, map: Identifier, west: Node|None, east: Node|None:

    if (map.name() != "map" and map.name() != "unordered_map":
        return None
    )

    args: mut:[Node] = []
    keys: mut:[Node] = []

    assertion: mut = quote(True)
    map_type: mut = None.Node
    
    for (kv in keyvals:
        type = quote(std.(unquote(map))<decltype(unquote(kv.args[0])),
                                        decltype(unquote(kv.args[1]))>)
        if (not map_type:
            map_type = type
        else:
            assertion = quote(unquote(assertion) and std.is_same_v<unquote(type),
                                                                   unquote(map_type)>)
        )
        args.append(quote({ unquote(kv.args[0], unquote(kv.args[1]) }))
        keys.append(kv.args[0])
    )

    comparator = lambda(a, b, a.equals(b))
    unsafe (:
        duplicate_iter = std.adjacent_find(keys.cbegin(), keys.cend(), comparator)
        if (duplicate_iter != keys.cend():
            # this won't catch all duplicate keys e.g. { 1 - 1: "zero", 0: "zero"}
            throw (std.runtime_error("duplicate keys in map literal"))
        )
    )

    # TODO with 'splice' (gh-2) this would be map_call = quote(unquote(map_type) { splice(args) }) 
    map_call = BracedCall(map_type, args)

    if (west:
        map_type = quote(unquote(west): unquote(map_type))
    )

    if (east:
        map_type = quote(unquote(map_type): unquote(east))
    )

    return quote(unquote(map_var): unquote(map_type) = lambda(:
        static_assert(unquote(assertion), "all key-value pairs must be of the same type in map literal")
        unquote(map_call)
    ) ())
)

class (Foo:
    x
)

def (main:
    # with macro:
    map: std.unordered_map = { 1: [Foo(1), Foo(2)], 2: [Foo(3)] }
    for ((key, vec) in map:
        std.cout << key << std.endl
        for (foo in vec:
            std.cout << foo.x
        )
    )

    # without macro:
    map2 = std.optional<std.map<int,int>> {}
    if (map2:
        std.cout << map2.at(42)  # std.optional autoderef  
    )
)
```

This is also available as a built-in in the standard library macros, see [include/convenience.cth](https://github.com/ehren/ceto/blob/main/include/convenience.cth).

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

#### Optionals + Variadics

In the first example of this readme the variadic pattern ```args``` does not greedily consume the optional ```stream_arg``` (the pattern with more matches is chosen)

#### Disabling Safety Checks

In our map-literal syntax example, iterating over a map, a C++ range-based-for is emitted because the iterable is a value and a reference to it doesn't escape between it's definition and the iteration. If the body of the for-loop might modify the iterable we fallback to indexing (to avoid UB from invalidated C++ iterators) with a static_assert that the container supports bounds checked random access indexing (fails for std.map). Container size changes during iteration result in ```std.terminate()```. Use ```unsafe_for``` to unconditionally emit a C++ range-based-for.

Want to claw back the performance and unsoundness of raw C++? The macro system can be used to modify safety defaults ("Every compiler flag is a bug" - Walter Bright):

```python
defmacro (for (i:type in iterable, block), i, type: Node|None, iterable, block: Block:
    iter_var_type = if (type:
        type
    else:
        # 'unsafe' context to use local of ref type still left to user
        # (this macro despite being dangerous still practices good safety hygene
        #  i.e. it wouldn't run afoul of potential macro_metavars_in_unsafe like checks)
        default_type: Node = quote(const:auto:ref)
        default_type
    )

    in_expr = quote(unquote(i): unquote(iter_var_type) in unquote(iterable))
    args: [Node] = [in_expr, block]
    return Call(quote(unsafe_for), args)
)

def (main:
    vec: mut = [1, 2, 3]

    for (i:int in vec:
        vec.append(i)  # ordinarily std.terminate() before the next iteration
        std.cout << i  # (but C++ UB with unsafe_for by default)
    )
)
```

Too powerful? There's a macro for that:

```python
defmacro(defmacro(args), args: [Node]:
    throw (std.logic_error("further macro definitions are banned"))
)

# error: further macro definitions are banned
# defmacro(2:
#     return quote(1)
# )
```

### Visitor Caveats / Class instances not "Smart References" / DLL Macro Implementation

Contrasting with the "Java style" / shared_ptr heavy visitor pattern shown earlier, the selfhost sources use a lower level version making use of C++ CRTP as well as the ```Foo.class``` syntax to access the underlying ```Foo``` in C++ (rather than ```shared_ptr<const Foo>```). This sidesteps the gotcha that ceto class instances aren't real "shared smart references" so **overriding** e.g. ```def (visit:override, node: BinOp)``` with ```def(visit: override, node: Add)``` is not possible because an **Add** (```std::shared_ptr<const Node>``` in C++) is not strictly speaking a derived class of ```std::shared_ptr<const BinOp>``` in C++. There are additional non-niceties using a shared_ptr managed ast hierarchy (including heavy handed implicit cloning) though it makes the defmacro side a little more pythonic. ```macro_matches``` below could be improved by taking a Node.class to lessen the shared_from_this-ing in the visitor callbacks (at the expense of more unary * in the body)

This code also demonstrates working with external C++ and more general/unsafe constructs like C++ iterators, raw pointers in combination with :unique classes, the C/C++ preprocessor, function pointers, and reinterpret_cast (and passing C++ types across dll boundaries, note: the C++ compiler used automatically by ceto during macro DLL compilation must match the one used during ```pip install``` to compile the [pybind11 bindings (selfhost/ast.ctp)](https://github.com/ehren/ceto/blob/main/selfhost/ast.ctp). Debug settings must match on Windows. This is an earlier version prior to alternational and optional matching ([selfhost/macro_expansion.cth](https://github.com/ehren/ceto/blob/main/selfhost/macro_expansion.cth)). We also need improvements like more fine grained patterns e.g. ```defmacro(foo(x), x: pattern(bar(y)), y:``` and better handling of greediness (implementation of 'splice' should only require python code changes...) plus general matching algorithm improvements though the slowest thing is the back and forth to Python with some unnecessary traversals on top which will be lessened by refactor/improvement of Scope handling allowing it to be available from macros (especially to distingush ```.``` attribute access from ```.``` implicit scope resolution (```::```) in a defmacro).

```python
include <map>
include <unordered_map>
include <ranges>
include <functional>
include <span>

include (ast)
include (visitor)
include (range_utility)

unsafe()

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
    parent: MacroScope.class:const:pointer = None

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

# We could perhaps start taking Node.class here (with more unary * in the body)
def (macro_matches, node: Node, pattern: Node, params: const:std.map<std.string, Node>:ref:
    std.cout << "node: " << node.repr() << " pattern: " << pattern.repr() << "\n"

    if (isinstance(pattern, Identifier):
        search = params.find(pattern.name().value())
        if (search != params.end():

            param_name = search->first
            matched_param = search->second
            if (isinstance(matched_param, Identifier):
                # wildcard match
                return std.map<std.string, Node>{{param_name, node}}
            elif (typeop = asinstance(matched_param, TypeOp)):
                param_type = typeop.rhs()

                # constrained wildcard / match by type
                if (isinstance(param_type, Identifier):
                    if ((param_type.name() == "BinOp" and isinstance(node, BinOp) or  # base class handling
                         param_type.name() == "UnOp" and isinstance(node, UnOp) or    # same
                         param_type.name() == "Node" or                               # redundant but allowed
                         node.classname() == typeop.rhs().name()):                    # exact match
                        return std.map<std.string, Node>{{param_name, node}}
                    )
                )
            )
        )
    )

    if (node.classname() != pattern.classname():
        return {}
    )

    if ((node.func == None) != (pattern.func == None):
        return {}
    )

    if (node.args.size() == 0 and node.func == None and pattern.func == None:
        if (node.equals(pattern):
            # leaf match
            return std.map<std.string, Node>{}
        )
        return {}
    )

    submatches: mut = std.map<std.string, Node> {}

    if (node.func:
        m = macro_matches(node.func, pattern.func, params)
        if (not m:
            return {}
        )
        submatches.insert(m.begin(), m.end())  # std::optional autoderef
    )

    pattern_iterator: mut = pattern.args.cbegin()
    arg_iterator: mut = node.args.cbegin()

    while (True:
        if (pattern_iterator == pattern.args.end():
            if (arg_iterator != node.args.end():
                # no match - no pattern for args
                return {}
            else:
                break
            )
        )

        subpattern: mut = *pattern_iterator

        if (isinstance(subpattern, Identifier):
            search = params.find(subpattern.name().value())

            if (search != params.end():
                param_name = search->first
                matched_param = search->second

                if (isinstance(matched_param, TypeOp):
                    if ((list_param = asinstance(matched_param.args[1], ListLiteral)):
                        # variadic wildcard pattern

                        if (list_param.args.size() != 1:
                            throw (SemanticAnalysisError("bad ListLiteral args in macro param"))
                        )

                        wildcard_list_type = list_param.args[0]
                        if (not isinstance(wildcard_list_type, Identifier):
                            throw (SemanticAnalysisError("bad ListLiteral arg type in macro param"))
                        )

                        wildcard_list_name = matched_param.args[0]
                        if (not isinstance(wildcard_list_name, Identifier):
                            throw (SemanticAnalysisError("arg of type ListLiteral must be an identifier"))
                        )

                        wildcard_type_op = TypeOp(":", [wildcard_list_name, wildcard_list_type]: Node)
                        wildcard_list_params: std.map<std.string, Node> = { {wildcard_list_name.name().value(), wildcard_type_op} }
                        wildcard_list_matches: mut:[Node] = []

                        while (arg_iterator != node.args.end():
                            arg = *arg_iterator
                            if (macro_matches(arg, wildcard_list_name, wildcard_list_params):
                                wildcard_list_matches.append(arg)
                            else:
                                break
                            )
                            arg_iterator += 1
                        )

                        submatches[param_name] = ListLiteral(wildcard_list_matches)

                        pattern_iterator += 1
                        if (pattern_iterator == pattern.args.end():
                            if (arg_iterator != node.args.end():
                                # no match - out of patterns, still have args
                                return {}
                            )
                            break
                        )
                        subpattern = *pattern_iterator
                    )
                )
            )
        )

        if (arg_iterator == node.args.end():
            if (pattern_iterator != pattern.args.end():
                # no match - out of args, still have patterns
                return {}
            )
            break
        )

        arg = *arg_iterator
        m = macro_matches(arg, subpattern, params)
        if (not m:
            return {}
        )
        submatches.insert(m.begin(), m.end())

        arg_iterator += 1
        pattern_iterator += 1
    )

    return submatches
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
        # std.cout << optional_str  # error: no autoderef without "."
        std.cout << optional_str.value()
    )

    # we have the billion dollar mistake like Python just no null-derefence UB
    # - better than a billion?.question?.marks??
    # optional_str.size()  # std.terminate()
)
```

As shown above no deref takes place when calling a method of ```std.optional```. That is, to call a method `value()` on the underlying value rather than the optional call `.value().value()`.

(this example also illustrates that for ceto classes and structs round parenthesese must be used e.g.  ```Foo(x, y)``` even though the generated code makes use of curlies e.g. ```Foo{x, y}``` (to avoid narrowing conversions). For external C++ round means round - curly means curly (```std.vector<int>(50, 50)``` is a 50 element vector of 50)

Note that to call the smart ptr `get` method (rather than a `get` method on the autoderefed instance) use ```unsafe((&obj)->get())``` or ```unsafe(std.addressof(obj)->get())```.

In addition, while we don't support deref without ```.``` one can add it implicitly in certain situations (note ```override``` caveats mentioned below when over-relying on smart pointers):

```python
class (Foo:

    def (operator("+"), foo:Foo:
        std.cout << "adding Foo and Foo\n"
        return self
    )

    def (operator("+"), other:
        std.cout << "adding Foo and other\n"
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
