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

# ^ refcounted template class with template method


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
defmacro(s.join(v), s: StringLiteral, v:
    return quote(string_join(unquote(v), unquote(s)))
)


# non-refcounted 
struct (Oops(std.runtime_error):
    pass  # inherited constructors
)


class (Holder:
    args
): unique  # non-refcounted but unique_ptr managed 
           # with implicit std::move from last use


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

    t:mut = std.thread(lambda(:       # lambda with no capture list:
        d = f.method(f).data_member   # - implicit strong capture for (non :unique) ceto 
                                      #   class instances only
        std.cout << if (d.size() < 100: d else: "too much data!"s) << std.endl
    ): void)

    # not macro invocation
    t.join()  

    holder = Holder(args)   # in C++: auto holder = make_unique<const decltype(Holder{args}) (args)
                            # instances of 'unique' type aren't const by default but they are ptr-to-const by default 
    holders: mut = []
    holders.append(holder)  # implict std.move from last use 

    std.cout << holders[0].args.size() << "\n"  # bounds checked vector access 
                                                # and unique_ptr autoderef
)
```

```
$ pip install ceto
$ ceto kitchensink.ctp a b c d e f
8
38
38
./kitchensink, a, b, c, d, e, f, end
8
```

## Features

### Use "." for method calls / attribute access and namespace access: no need for `->` or `*` in safe code

`.` performs C++ scope resolution (`::` can still be used if desired), `std::shared_ptr`, `std::unique_ptr`, and `std::optional` autoderef in addition to ordinary C++ member access. Autoderef works by compiling a generic / non-type-annotated function like

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

where `ceto::mad` (maybe allow deref) forwards `f` unchanged (allowing the dereference via `*` to proceed) when `f` is a smart pointer or optional, and otherwise returns the `std::addressof` of `f` to cancel the outer `*` dereference for anything else (equivalent to ordinary attribute access `f.foo()` in C++). This is adapted from this answer: https://stackoverflow.com/questions/14466620/c-template-specialization-calling-methods-on-types-that-could-be-pointers-or/14466705#14466705 except the ceto implementation (see include/ceto.h) avoids raw pointer autoderef (you may still use `*` and `->` in ceto when working with raw pointers). When `ceto::mad` allows a dereference, it also performs a throwing nullptr check (use `->` for an unsafe unchecked access).

## More Examples

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

You can code a simple visitor pattern just like\* Java

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

'Just like Java' (with differerent syntax and the complication of const/mut) because the two crucial method calls of the visitor pattern above are written

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

At this point, you might be objecting on performance grounds alone. While the above visitor example 

While this is true (though we claim zero overhead because you can always avoid `class`


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

