# ceto

**ceto** is an experimental "pythonish" dialect of C++:

```python

include <numeric>
include <thread>
include <ranges>
include <string>
include <iostream>


class (Foo:
    s  # implicit template with an implicit (but explicit in C++ sense) 1-arg constructor (deleted default constructor)

    def (method, param:  # const by default method with const T& param
        # call to .size() is maybe an ordinary C++ '.' access, or maybe it's a null-checked (throwing) smart pointer or std::optional autoderef!
        std.cout << "size: " << param.size()  << "\n"
        return self  # implicit shared_from_this
    )

    def (size:
        return self.s.size()
    )
)


def (string_join, sep: std.string, v: [std.string]:  # string params (and various other things) always passed by const:ref
    static_assert(std.is_same_v<decltype(sep), const:std.string:ref>)
    static_assert(std.is_same_v<decltype(v), const:std.vector<std.string>:ref>)

    if (v.empty():
        return ""s
    )

    return std.accumulate(v.cbegin() + 1, v.cend(), v[0],
        lambda[&sep] (a, b, a + sep + b))
): std.string  # as a return type this is just std::string


# arbitrary expression macros - use wisely!
defmacro(s.join(v), s: StringLiteral, v:
    return quote(string_join(unquote(s), unquote(v)))
)


def (main:
    s : mut = []

    for (i in std.ranges.iota_view(0, 10):
        s.append(std.to_string(i))
    )

    description = ", ".join(s) + if (s.size() > 5: " that's a lot of elements!" else: "")

    f = Foo(description)

    t: mut = std.thread(lambda(:
        # shared/weak ceto defined class instances (or simple is_arithmetic_v variables) captured by value implicitly  - everything else e.g. std.string/std.vector requires an explicit capture list (see above)
        std.cout << f.method(f).s << std.endl  # note that call to 'size' for generic 'param' of 'method' relies on autoderef
    ): void)

    f.method(s)  # call to 'size' in method invokes std::vector::size - non-deref case

    opt: std.optional<std.string> = description
    f.method(opt)  # call to 'size' in method uses std::optional autoderef

    t.join()
)

# Output: 
# size: 10
# size: 54
# size: 54
# 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 that's a lot of elements!

```

