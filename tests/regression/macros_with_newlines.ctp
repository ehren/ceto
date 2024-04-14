# Test Output: Hello
# Test Output: World

include <iostream>
include <cstdlib>


defmacro (with_newlines (:
    args
), args: [Node]:  
    new_args: mut:[Node] = []

    # TODO should use arg: [LeftShiftBinOp]  (need a dedicated ast node for it)
    # might also want a dedicated function like ZeroOrMore(std.cout << arg, arg) for a more fine grained pattern?
    for (a in args:
        new_args.append(quote(unquote(a) << "\n"))
    )

    new_block = Block(new_args)

    # need a simple 'scope' special form
    #l = quote(lambda[ref] (unquote(new_block)))  # this doesn't work because of "helpful" "lambda returns last arg automatically" behavior. similar probs with if stmts
    #return quote((lambda[ref] (unquote(new_block)): void) ())  # still fails
    #return quote(if (1, unquote(new_block)))  # similar probs ("bad first if arg") (think it's a one-liner if...)

    # workaround
    call_args: [Node] = [new_block]
    l = Call(quote(lambda[ref]), call_args)
    return quote(unquote(l)())

    # this also works (while loops aren't subject to the hardcoded dubious transformations that should be macros in semanticanalysis.py)
    #new_args.append(quote(break))
    #new_block = Block(new_args)
    #return quote(while(true, unquote(new_block)))
)


def (main:
    with_newlines (:
        std.cout << "Hello"
        std.cout << "World"
    )
)
