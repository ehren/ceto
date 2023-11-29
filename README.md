# ceto

**ceto** is an experimental "pythonish" dialect of C++:

```python
include <numeric>
include <thread>
include <ranges>
include <iostream>


class (Foo:
    data_member

    def (method, param:
        std.cout << "size: " << param.size()  << "\n"
        return self
    )

    def (size:
        return self.data_member.size()
    )
)


def (string_join, vec: [std.string], sep = ", "s:   # string params (and various other things) always passed by const:ref
    static_assert(std.is_same_v<decltype(sep), const:std.string:ref>)
    static_assert(std.is_same_v<decltype(vec), const:std.vector<std.string>:ref>)

    if (vec.empty():
        return ""s
    )

    # unsafe lambda ref capture requires an explicit capture list. 
    # The untyped lambda params 'a' and 'b' are const:auto:ref by default
    # (like the generic param of 'method' above)
    return std.accumulate(vec.cbegin() + 1, vec.cend(), vec[0],
        lambda[&sep] (a, b, a + sep + b))
): std.string  # as a return type this is just std::string


# arbitrary expression macros - use carefully!
defmacro(s.join(v), s: StringLiteral, v:
    return quote(string_join(unquote(v), unquote(s)))
)


def (main, argc: int, argv: const:char:ptr:const:ptr:
    args : mut = []  # inferrable from .append call 
                     # (thanks to logic derived from https://github.com/lukasmartinelli/py14)

    for (a in std.span(argv, argc):
        args.append(std.string(a))
    )

    # macro invocation (and expression if)
    summary = ", ".join(args) + if (args.size() > 5: " that's a lot of arguments!" else: "")

    f = Foo(summary)  # really make_shared<const decltype(Foo{summary})>(summary) - note extra CTAD!
                      # - don't grab the pichforks yet, there's 'struct'
                      #   (and 'unique' with implicit std.move from last use!).

    f.method(args)  # this call to 'method' is a null checked shared_ptr autoderef.
                    # The call to 'size' in method, however, invokes std::vector::size (no deref).
                    # For a non null checked call to method (with potential UB!) write f->method(args)

    # two autoderefs (call to 'method' and 'size':
    f.method(f)    

    opt: std.optional<std.string> = summary
    if (opt:
        std.cout << opt.size() << " (optional autoderef)\n"
        # ^ autoderef works by transforming ordinary method calls using '.' to something like
        # maybe_allow_deref(opt)->size() where maybe_allow_deref returns opt unchanged if
        # it's a std::optional or smart pointer. For anything else, maybe_allow_deref returns 
        # the real std::addressof of its argument (cancelling out the outer deref. See ceto.h)

        f.method(opt)  # call to 'size' in the generic 'method' is also a std::optional autoderef
    )

    t: mut = std.thread(lambda(:
        # shared/weak ceto defined class instances (or simple is_arithmetic_v variables) are captured 
        # by value implicitly - everything else e.g. std.string/std.vector requires an explicit capture list (see above)
        std.cout << f.method(f).data_member << "\n"
        std.cout << "use count: " << (&f)->use_count() << std.endl  # one way to get around the autoderef and invoke the 
                                                                    # underlying methods of std::shared_ptr (as a bonus, 
                                                                    # the use of explicit "&" and "->" signals unsafety).
                                                                    # Note: smart pointers are autoderefed, raw pointers are not!
    ): void)  # lambdas automatically return their last expression 
              # unless that expression is_void_v or the return type is_void_v

    # you may still call the methods of std::optional (rather than the wrapped type) without additional ceremony:
    std.cout << opt.value().size() << " (no optional autoderef)\n"

    # not a macro invocation
    t.join()
)
```

```
$ ceto kitchensink.ctp a b c d e f
size: 7
60 (optional autoderef)
size: 60
60 (no optional deref)
size: 60
./kitchensink, a, b, c, d, e, f that's a lot of arguments!
use count: 2
```

## More Examples:

Classes definitions are intended to resemble python dataclasses

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

You can code a simple visitor pattern almost like\* Java

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

