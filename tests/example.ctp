include <numeric>
include <ranges>
include <iostream>
include <future>

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

class (UniqueFoo:
    consumed: [UniqueFoo] = []

    def (size:
        return self.consumed.size()
    )
    
    def (consuming_method: mut, u: UniqueFoo:
        # u is a (passed by value) unique_ptr<const UniqueFoo> in C++
        Foo(42).method(u)  # Note that generic (non-type annotated) parameters (like 'param' above) are implicitly const:ref
        self.consumed.push_back(u)   # Automatic std::move from last use of 'u'
    )
) : unique

struct (Oops(std.runtime_error):
    pass
)

def (string_join, vec: [std.string], sep = ", "s:
    # std.string, std.vector and various other things passed by const:ref by default
    static_assert(std.is_same_v<decltype(vec), const:std.vector<std.string>:ref>)
    static_assert(std.is_same_v<decltype(sep), const:std.string:ref>)

    if (vec.empty():
        return ""
    )

    return std.accumulate(vec.cbegin() + 1, vec.cend(), vec[0],
        lambda[&sep] (a, b, a + sep + b))
): std.string  # as a return type (or a class member) it's by value

defmacro (s.join(v), s: StringLiteral, v:
    return quote(string_join(unquote(v), unquote(s)))
)

def (main, argc: int, argv: const:char:ptr:const:ptr:
    args: mut = []

    for (a in std.span(argv, argc):
        args.append(std.string(a))
    )

    args.append(if (argc == 0:
        "no args"s
    elif argc > 15:
        throw (Oops("too many args entirely"))
    else:
        "end"s
    ))

    summary = ", ".join(args)

    f = Foo(summary)  # equivalent to C++: const auto f = make_shared<const decltype(Foo{summary}) (summary)
    f.method(args)    # autoderef
    f.method(f)       # autoderef also in the body of 'method'
    calls_method(f)   # autoderef in the body of 'calls_method'

    i = 42u
    fut: mut = std.async(std.launch.async, lambda(:
        # Implicit copy capture (no capture list specified) for shared/weak instances, arithmetic types, 
        # and enums only (but not pointers or expensive to copy things)
        data = f.method(f).data_member
        if (data.size() + i < 1000: data else: "too much data!"s)
    ))

    std.cout << fut.get()

    u: mut = UniqueFoo()
    u2 = UniqueFoo()
    u.consuming_method(u2)  # auto std.move from last use of u2
    u.consuming_method(u)   # same (i.e. same as CETO_AUTODEREF(u).consuming_method(std::move(u)) in C++)
)
