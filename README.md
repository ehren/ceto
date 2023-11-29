# ceto

**ceto** is an experimental "pythonish" dialect of C++:

```python

include <numeric>
include <thread>
include <ranges>
include <string>
include <iostream>


def (string_join, sep: std.string, v: [std.string]:  # string params (and various other things) always passed by const:ref
    static_assert(std.is_same_v<decltype(sep), const:std.string:ref>)
    static_assert(std.is_same_v<decltype(v), const:std.vector<std.string>:ref>)

    if (v.empty():
        return ""s
    )
    
    return std.accumulate(v.cbegin() + 1, v.cend(), v[0],
        lambda[&sep] (a, b, a + sep + b))
): std.string  # as a return type this is just std::string


class (Foo:
    s  # implicit template with an implicit (but explicit in C++ sense) 1-arg constructor (deleted default constructor)

    def (method:  # const by default method
        return self  # implicit shared_from_this
    )
)


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
        std.cout << f.method().s  # lambdas without an explicit capture list capture class instances by value (+1 refcount)
    ): void)

    t.join()
)

# Output: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 that's a lot of elements!


```

