defmacro (print(args, stream_arg), args:[Node], stream_arg: Assign|None:

    decorate_error: mut = False

    stream = if (stream_arg:
        if (stream_arg.equals(quote(file = std.cerr)):
            decorate_error = True
            quote(std.cerr)
        elif stream_arg.args[0].equals(quote(file)):
            rhs = stream_arg.args[1]
            if (isinstance(rhs, StringLiteral):
                # we'll be nice and open a file in append mode for you
                quote(std.ofstream(unquote(rhs), std.ios.app))
            else:
                rhs
            )
        else:
            throw (std.invalid_argument('unexpected "keyword argument": ' + stream_arg.repr()))
        )
    else:
        quote(std.cout)
    )    

    result: mut = stream

    if (decorate_error:
        result = quote(unquote(result) << "🙀")
    )

    for (arg in args | std.views.take(std.ssize(args) - 1):
        result = quote(unquote(result) << unquote(arg))
    )

    # add a newline but try to avoid a double newline
    last = if (args.size() and (args.back().equals(quote(std.endl)) or (
               isinstance(args.back(), StringLiteral) and args.back().str.ends_with('\n'))):
        args.back()
    elif args.size():
        quote(unquote(args.back()) << std.endl)
    else:
        quote(std.endl)
    )

    return quote(unquote(result) << unquote(last))
)

def (main:
    a:mut = "a"
    print()
    print(a)
    print(a, a)
    print(a, a, file=std.cerr)

    print(a,file=std.cerr)
    print(a, file=std.cerr)
    print()
    print("aa\n", file=std.cerr)
    print("aa\n\n", file=std.cerr)
    print(a, file=std.cerr)
    #print((a="c"))
)


