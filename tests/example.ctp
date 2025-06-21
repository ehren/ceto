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
        Foo(42).method(u)  # u passed by const:ref (to a method taking a generic param)
        self.consumed.push_back(u)   # Automatic std::move from last use of 'u'
    )
) : unique

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

    args = [std.string(a), for (a in std.span(argv, argc))]

    summary = ", ".join(args)

    f = Foo(summary)  # in C++ f is a const std::shared_ptr<const Foo<decltype(summary)>>
    f.method(args)    # autoderef
    f.method(f)       # autoderef also in the body of 'method'
    calls_method(f)   # autoderef in the body of 'calls_method'

    fut: mut = std.async(std.launch.async, lambda(:

        # Implicit copy capture (no capture list specified) for shared/weak
        # ceto-class instances, arithmetic types, and enums only.
        # Prefer capture lists for anything useful despite safety/verbosity gotchas?
        # Just add:
        # defmacro (lambda(args), args: [Node]:
        #     block = Block(args)
        #     return quote(lambda[] (block))
        # )

        f.method(f).data_member
    ))

    std.cout << fut.get()

    u: mut = UniqueFoo()
    u2 = UniqueFoo()
    u.consuming_method(u2)  # implicit std.move from last use of u2 (because :unique)
    u.consuming_method(u)   # in C++: CETO_AUTODEREF(u).consuming_method(std::move(u))
)
