# Test Output: 1
# Test Output: 2
# Test Output: a
# Test Output: [1, 2, 3, ]


include <iostream>


defmacro (log_with_break (:
    args
), args: [Node]:
    new_args: mut:[Node] = []

    for (a in args:
        if (a.name() == "break":
            new_args.append(a)
        elif isinstance(a, ListLiteral):
            new_args.append(quote(std.cout << "["))
            for (i in a.args:
                new_args.append(quote(std.cout << unquote(i) << ", "))
            )
            new_args.append(quote(std.cout << "]\n"))
        else:
            new_args.append(quote(std.cout << unquote(a) << "\n"))
        )
    )

    new_args.append(quote(break))
    new_block = Block(new_args)
    return quote(while(true, unquote(new_block)))
)


def (main:
    log_with_break (:
        1
        2
        "a"
        [1, 2, 3]
        break
        "b"
    )
)
