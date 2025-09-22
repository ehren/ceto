defmacro (print(args), args: [Node]:
    if (args.size():
        call = asinstance(args[0].parent().parent(), Call)
        if (call and call.func.name() == "defmacro":
            # ignore print(...) as a pattern arg in a defmacro (TODO should we handle this for the user automatically?)
            return None
        )
    )

    # Let the existing macro handle the implementation

    # TODO with splice:
    # return quote(print(splice(args), file=std.cout))

    # without splice:
    new_args: mut = args
    new_args.append(quote(file=std.cout))
    return Call(quote(print), new_args)
)

defmacro (print(args, file=optional_stream), args: [Node], file: Identifier, optional_stream: Node|None:
    stream = if (optional_stream:
        optional_stream
    else:
        quote(std.cout)
    )

    result: mut = stream

    if (optional_stream and optional_stream.equals(quote(std.cerr)):
        result = quote(unquote(result) << "🙀")
    )

    for (arg in args:
        result = quote(unquote(result) << unquote(arg))
    )

    if (not optional_stream:
        # 'file' is an Identifier in the source to be printed (not a stream arg)
        result = quote(unquote(result) << unquote(file))
    )

    return quote(unquote(result) << std.endl)
)

def (main:
    a = "a"
    print(a)
    print(a, a)
    print(a, a, file=std.cerr)
    print("b", file=std.cerr)
    print("b")
    print(file=std.cerr)
    print()
)
