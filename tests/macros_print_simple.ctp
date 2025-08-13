defmacro (print(args), args: [Node]:
    if (args.size() == 0:
        return quote(std.cout << std.endl)
    )

    output: mut = args[0]

    for (arg in args | std.views.drop(1) | std.views.take(std.ssize(args) - 2):
        output = quote(unquote(output) << unquote(arg))
    )

    last = args[args.size() - 1]

    stream = if (last.equals(quote(file = std.cerr)):
        output = quote("🙀" << unquote(output))
        quote(std.cerr)
    elif isinstance(last, Assign) and last.args[0].equals(quote(file)):
        rhs = last.args[1]
        if (isinstance(rhs, StringLiteral):
            throw (std.invalid_argument("Invalid string arg "s + last.repr() + (
                                        ". Use std.ofstream instead.")))
        )
        rhs
    elif args.size() == 1:
        quote(std.cout)
    else:
        output = quote(unquote(output) << unquote(last))
        quote(std.cout)
    )

    return quote(unquote(stream) << unquote(output) << std.endl)
)

def (main:
    x: mut = []
    x.append(5)
    print(x[0], file=std.ofstream("example.txt"))
)
