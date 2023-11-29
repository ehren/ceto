# ceto

**ceto** is an experimental "pythonish" dialect of C++:

```python
include <numeric>
include <thread>
include <ranges>
include <iostream>


class (Foo:
    data_member  # implicit template with an implicit (but explicit in C++ sense) 
                 # 1-arg constructor (deleted default constructor)

    def (method, param:  # const by default method with const T& param
        # call to .size() is maybe an ordinary C++ '.' access, 
        # or maybe it's a null-checked (throwing) smart pointer or std::optional autoderef!
        std.cout << "size: " << param.size()  << "\n"
        return self  # implicit shared_from_this
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

    return std.accumulate(vec.cbegin() + 1, vec.cend(), vec[0],
        lambda[&sep] (a, b, a + sep + b))
): std.string  # as a return type this is just std::string


# arbitrary expression macros - use carefully!
defmacro(s.join(v), s: StringLiteral, v:
    return quote(string_join(unquote(v), unquote(s)))
)


def (main, argc: int, argv: const:char:ptr:const:ptr:
    args : mut = []  # no need for the type if inferrable from .append call 
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
                                                                    # the use of explicit "&" and "->" signals unsafety)
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



