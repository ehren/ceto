# ceto

**ceto** is an experimental programming language transpiled to C++ but inspired by Python in variable declaration style, \*syntax, safe(ish) reference semantics for `class`, and generic programming as an exercise in forgetting the type annotations. Every special control structure is a function call.

```python
include <numeric>
include <thread>
include <ranges>
include <iostream>

class (Foo:
    data_member

    def (method, param:
        std.cout << param.size()  << "\n"
        return self
    )

    def (size:
        return self.data_member.size()
    )
)

def (calls_method, f:
    return f.method(f)
)

def (string_join, vec: [std.string], sep = ", "s:
    # std.string and various other things passed by const ref
    static_assert(std.is_same_v<decltype(vec), const:std.vector<std.string>:ref>)
    static_assert(std.is_same_v<decltype(sep), const:std.string:ref>)

    if (vec.empty():
        return ""
    )

    # unsafe lambda ref capture requires capture list
    # untyped params a, b (like 'param' above) are implicitly const:auto:ref
    return std.accumulate(vec.cbegin() + 1, vec.cend(), vec[0],
        lambda[&sep] (a, b, a + sep + b))

): std.string  # as a return type (or a class member) it's by value

# arbitrary expression macros - use carefully!
defmacro (s.join(v), s: StringLiteral, v:
    return quote(string_join(unquote(v), unquote(s)))
)

# non-refcounted 
struct (Oops(std.runtime_error):
    pass  # inherited constructors
)

class (UniqueFoo:
    consumed: [UniqueFoo] = []
    
    def (consuming_method: mut, u: UniqueFoo:  # u is a (passed by value) unique_ptr<const UniqueFoo> in C++
        self.consumed.push_back(u)   # automatic std::move from last use 
    )

    def (size:
        return self.consumed.size()
    )

) : unique

def (consuming_function, u: UniqueFoo:
    Foo(42).method(u)  # u passed by const:ref here
    std.cout << u.consumed.size() << std.endl
)

def (main, argc: int, argv: const:char:ptr:const:ptr:
    args: mut = []  # no need for the list type 
                     # - inferred from 'append' thanks to logic of 
                     #   https://github.com/lukasmartinelli/py14

    for (a in std.span(argv, argc):
        args.append(std.string(a))
    )

    # all special forms are expressions
    more = if (argc == 0:
        "no args"s
    elif argc > 15:
        throw (Oops("too many args entirely"))
    else:
        "end"s
    )
    args.append(more)

    # macro invocation
    summary = ", ".join(args)

    f = Foo(summary)  # equivalent to C++: const auto f = make_shared<const decltype(Foo{summary}) (summary)
    f.method(args)    # autoderef
    f.method(f)       # autoderef also in the body of 'method'
    calls_method(f)   # autoderef in the body of 'calls_method'

    t:mut = std.thread(lambda(:       # lambda with no capture list:
        d = f.method(f).data_member   # - implicit strong capture for (non :unique) ceto 
                                      #   class instances only
        std.cout << if (d.size() < 100: d else: "too much data!"s) << std.endl
    ): void)

    # not macro invocation
    t.join()  

    u: mut = UniqueFoo()
    u2 = UniqueFoo()
    u.consuming_method(u2)  # implic std::move from last use of u2
    u3: UniqueFoo = u  # implicit std::move from last use of u (note that consuming_function takes a UniqueFoo and not a UniqueFoo:mut)
    consuming_function(u3)  # implicit std::move from last use
)
```

## Usage

```bash
$ pip install ceto
$ ceto example.ctp
5
29
29
29
./tests/example, a, b, c, end
1
1
```

## Features

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

where `ceto::mad` (maybe allow deref) forwards `f` unchanged (allowing the dereference via `*` to proceed) when `f` is a smart pointer or optional, and otherwise returns the `std::addressof` of `f` to cancel the outer `*` dereference for anything else (equivalent to ordinary attribute access `f.foo()` in C++). This is adapted from this answer: https://stackoverflow.com/questions/14466620/c-template-specialization-calling-methods-on-types-that-could-be-pointers-or/14466705#14466705 except the ceto implementation (see include/ceto.h) avoids raw pointer autoderef (you may still use `*` and `->` when working with raw pointers). When `ceto::mad` allows a dereference, it also performs a throwing nullptr check (use `->` for an unsafe unchecked access).


### Less typing (at least as in your input device\*)

This project uses many of the ideas from the wonderful https://github.com/lukasmartinelli/py14 project such as the implicit insertion of *auto* (though in ceto it's implict *const auto* for untyped locals and *const auto&* for untyped params). The very notion of generic python functions as C++ template functions is also largely the same (including our backend implementation). 

We've also derived our code generation of Python like lists as *std.vector* from the project.

For example, from the [README](https://github.com/lukasmartinelli/py14?tab=readme-ov-file#how-it-works):

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

Though, we require a *mut* annotation and rely on *std.ranges*, the wacky forward inference via *decltype* to codegen the type of results above as *std::vector<decltype(fun(std::declval<std::ranges::range_value_t<decltype(values)>>()))>*  derives from the py14 implementation.
	

(*tempered with the dubiously attainable goal of less typing in the language implementation)


### Classes, Inheritance

Class definitions are intended to resemble Python dataclasses

```python
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

def (main:
    f = Generic("5")
    f2 = Concrete(5)
    #f2e = Concrete("5")  # error
    f3 = Generic2([5], 5.0)
    std.cout << f.x << f2.x << f3.x[0]
)

# Output: 555.0

```

You can code a simple visitor pattern just like\* Java (see GOTCHAs)

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
            arg.accept(self)
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

#def (foo, (x, y):   # maybe TODO
def (foo, tuple1: (int, int), tuple2 = (0, 1):
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

    for ((x, y) in tuples:
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
            while (true:
                std.this_thread.sleep_for(std.chrono.seconds(1))
                if ((s = w.lock()):
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


## Gotchas

In the "just like Java" visitor example we write

```python
visitor.visit(self)
```

rather than 

```
visitor.visit(*this)
```

This relies on the meaning of *self*. For simple attribute accesses `self.foo` is rewritten to `this->foo`. When `self` is used in other contexts (including any use in a capturing lambda) a `const` definition of `self` using `shared_from_this` is provided to the body of the method (compile time error when used with *struct* or *:unique* instances and TODO a transpile time error when non-trivial use of *self* occurs in *init*).

There are performance concerns with the hidden use of *shared_ptr* in this visitor example which we discuss below (TODO) however a more pressing problem with this example is that ceto class instances aren't real "smart references". That is, they're not C++ references backed by a refcount that behave the same as ordinary C++ references with respect to function overloading especially). 

In particular, this means that

```python
def (visit: override: mut, node: BinOp:
    ...
)

```

is not overridden by 

```python
def (visit: override: mut, node: Add:
    ...
)

```

A note on development status: we are partially selfhosted but only by cheating! That is, we've implemented an ast in ceto then briged it to our original python bootstrap compiler via the pybind11 bindings here.

For our "selfhost" ast (TODO link), we heavily rely on (shared) ceto class instances (primarily to integrate with our bootstrap python compiler via the pybind11 bindings here (TODO link). Using :unique classes for our ast nodes would have certain benefits in the future

(Though an implementation of our ast using :unique is possible in the future, 

   integration with our exising to be replaced   (for  a (TODO link) CRTP visitor implementation that relies on overriding visit Node.


TODO: clean up and integrate the below text better

"Just like Java" (with differerent syntax and the complication of const/mut) because the two crucial method calls of the visitor pattern above are written

```python
arg.accept(self)  # java equivalent: arg.accept(this)
```

and

```python
visitor.visit(self)  # java equivalent: visitor.visit(this)
```

rather than the the idiomatic C++ which would be something like

```c++
visitor.visit(*this)
``` 

This brings us to the meaning of `self`: For simple attribute accesses `self.foo` is rewritten to `this->foo`. When `self` is used in other contexts (including any use in a capturing lambda) a `const` definition of `self` using `shared_from_this` is provided to the body of the method.

At this point, you might be saying "automatic make_shared, and automatic shared_from_this??!" This would be slower than Java! (at least once the JVM starts up)"

To alleviate these performance concerns, we can first change the definition of `Visitor` and `SimpleVisitor` to use `struct` instead of `class`. We would then change calls in the `visit` methods like `arg.accept(self)` to `arg.accept(*this)  # note *self works but might cause an unnecessary refcount bump`. `accept` methods must be changed so that `Visitor` (now just a `struct`) is passed by `mut:ref` rather than just `mut` (note that when `Visitor` was a (non-`unique`) `class`, `Visitor:mut` as a function param meant in C++ `const std::shared_ptr<Visitor>&` (that is a const-ref shared_ptr to non-const)

Note that these changes introducing unary `*` as well as the keyword `ref` (especially `mut:ref` !) might require an `unsafe` block in the future (cost of performance).

We're then left with `Node` and its derived classes. If changed to `struct` we'll be forced to redesign this class (err struct) hierarchy either in terms of raw pointers or of explicitly smart pointer managed instances. Smart pointer managed struct instances still benefit from autoderef; that is `arg.accept` is never required to be rewritten `arg->accept` unless one is unwisely avoiding a null check). 

For ceto's selfhost ast implementation we define the visitor pattern using struct but (for better or worse) keep the class hierarchy as shared (for compatibility with our existing python bootstrap compiler). However we define the visitor pattern visit methods without smart pointer parameter passing by using 'Node.class' to get at the underlying class (just `Node` in C++). This also requires changing the accept methods to call `visitor.accept(*this)`. Note that like struct instances, a `Foo.class` is still passed by `const:ref` automatically.

See here for our ast
Here for our visitor implmentation and a CRTP visitor subclass for visiting only certain derived classes conveniently (stolen from symengine)
See here for our macro expansion pass which uses the CRTP utility (and also has a bit of everything e.g. `MacroScope` is `:unique` and we rely on all 3 kinds - shared, unique, and optional too.

There is also the possibility to define the `Node` hierarchy using `unique`. The 'smart ptr heavy' version of the visitor pattern would then benefit from our handling of `const:Node:ref` in a function param (when `Node` is `:unique`) as `const unique_ptr<const Node>&` (there is not such a convenient way to operate with non-ptr-to-const unique_ptr managed instances passed by const ref - nor is there a convenient way to operate with non-const references to smart pointers - as an intended safety feature!)

While you are right, this is not the worst thing with the above visitor example! When making slightly more complicated use of the visitor pattern you'll quickly realize that  

```python
def (visit: override: mut, node: BinOp:
    ...
)

```

is not "overridden" by 

```python
def (visit: override: mut, node: Add:
    ...
)

```


At this point, you might be objecting on performance grounds alone. While the above visitor example 

While this is true (though we claim zero overhead because you can always avoid `class`


-----

### Further Explanation


## Features

- [x] Autoderef (call methods on "class instances" using `.` instead of `->`)
   - [x] Using dot on a std::shared_ptr, std::unique_ptr, or std::optional autoderefed (in the case of std::optional no deref takes place when calling a method of std::optional - that is, to call a method `value()` call `.value().value()`). For std::shared/unique_ptr you must use a construct like `(&o)->get` to call the smart ptr `get` method.
- implicit scope resolution using `.` (`::` may still be used)
- auto make_shared / make_unique for ceto defined classes (with hidden CTAD for templated classes). Write `f = Foo(x, y)` like python regardless of whether `Foo` is a (unique) class or struct (and regardless of whether `Foo` has generic/untyped data members or is an explicit template).
- (const) auto everywhere and nowhere
    - locals `const:auto` by default
    - parameters `const` by default and maybe `const:ref` by default depending on their type (for example all shared_ptrs transparently managing ceto defined class instances are passed by const ref, all ceto defined structs are passed by `const:ref`, as well as `std::vector` and `std::tuple` when using the ceto python style `[list, literal]` and `(tuple, literal)` notation)
    - methods const by default
- `:` as a first class binary operator in ceto for use by macro defined or built-in constructs e.g. one-liner ifs `if (cond: 1 else: 0)`. Variable type declaration syntax mimicks python type annotations e.g. `x: int` but `:` acts as a type separator character for multi-word C++ types (and type-like / space separated things) e.g. `x: static:std.array<unsigned:int, 4> = {1, 2, 3, 4}`

## Features

- [x] Autoderef (call methods on class instances using `.` instead of `->` or `*`)
    - [x] `.` performs  `std::shared_ptr`, `std::unique_ptr`, and `std::optional` autoderef in addition to ordinary C++ member access. 
- [x] `.` performs C++ scope resolution (like namespace access in Python)

----

Extended Feature List
- [x] Autoderef (call methods on 'class instances' using '.' instead of '->')
   - [x] Might as well autoderef every smart pointer and optionals too. Except, when calling a method of std::optional, yo
- implicit scope resolution using `.` (`m: std.unordered_map<int, int> = {{0,1}}` but you can still write `m: std::unordered_map<int, int>` if you insist
- auto make_shared / make_unique for ceto defined classes (with hidden CTAD for templated classes)
- (const) auto everywhere and nowhere
    - locals `const:auto` by default
    - parameters `const` by default and maybe `const:ref` by default depending on their type (for example all shared_ptrs transparently managing ceto defined class instances are passed by const ref, all ceto defined structs are passed by `const:ref`, as well as `std::vector` and `std::tuple` when using the ceto python style `[list, literal]` and `(tuple, literal)` notation)

    - methods
- `:` as a first class binary operator in ceto (for creation of user defined constructs in the macro system and some tom foolery in built-in ceto constructs like one-liner ifs `if (cond: 1 else: 0)`. Types are annoted with 


Informally, one can think of the language as "Python with two parenthesese moved or inserted" (per control structure). This is a good approach for those less familliar with C++, for those wanting to avoid certain explicitly unsafe C++ operations such as unary `*` (present in C++/ceto but not Python and which might TODO require an `unsafe` block in in the future), and for those wishing to prototype with Python style ceto (heavily using `class`) with an easier path to integrating more precise/performant C++ (whether ceto defined or not) later.

## Syntax: 

Every Python statement is present but represented as a function call that takes zero or more indented blocks in addition to any ordinary parameters. Blocks begin with an end of line `:`. Every other occurence of `:` is a first class binary operator (TypeOp in the ast). The other operators retain their precedence and syntax from C++ (see https://en.cppreference.com/w/cpp/language/operator_precedence) with the exceptions of `not`, `and`, and `or` which require the Python spelling but C++ precedence. Some C++ operators such as pre-increment and post-increment are intentionally not present (you can't have a fake Python with `++`).

`def`, `class`, `while`, `for`, `if`, `try`, etc are merely `Identifier` instances in the ast (and macro system) not special keywords in the grammar.

Simple python expressions such as `[list, literals]`, `{curly, braced, literals}` and `(tuple, literals)` are present as well as array[access] notation. We also support C++ templates and curly braced calls.

For example:

```python
include <cassert>  # parsed as templates
include <unordered_map>
include <optional>

def (main:
    s = [1, 2]  # ast: Assign with rhs a ListLiteral
    
    for (x in {1, 2, 3, 4}:  # ast: BracedLiteral as rhs of InOp and first arg to call with func "for" (second arg a Block)
        pass
    )

    m: std.unordered_map<int, std.string> = {{0, "zero"}, {1, "one"}}
    m2 = std.unordered_map <int, std.string> {{0, "zero"}, {1, "one"}}
    assert(m == m2)

    v = std.vector<int> {1, 2}  # ast: BracedCall with func a Template
    v2: std.vector<int> = {1, 2}
 
    assert(v == v2)
    assert(v == s)

    v3: std.vector<int> (1, 2)  # ast: Call with func a template
    assert(v != v3)
    assert(v3.size() == 1 and v3[0] == 2)

    opt: std.optional<std.string> = {}  # empty
    if (opt:
        assert(opt.size() >= 0)  # aside: std.optional autoderef here
    )

    it:mut = s.begin()
    it.operator("++")(1)   # while there's no ++ and -- you can do this
    it.operator("--")()    # or this (which one is the preincrement anyway?)
    cpp"
        --it--  // if you really insist
        #define PREINCREMENT(x) (++x)  // even worse
    "
    PREINCREMENT(it)
    
    # of course the pythonic option should be encouraged
    it += 1  

    # note the utility of ++ is diminished when C-style for loops are unavailable anyway
    assert(it == s.end())
)

```

