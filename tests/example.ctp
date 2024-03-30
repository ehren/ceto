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
    consuming_function(u)   # implicit std::move from last use
)
