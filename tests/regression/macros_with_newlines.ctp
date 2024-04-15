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
    #return quote(if (1, unquote(new_block)))  # this works fine
    return quote(if (1, unquote(new_block)): constexpr)  # should silence any potential constant comparison warnings?

    #new_args.append(quote(return))
    #new_block = Block(new_args)
    #return quote(lambda[ref] (unquote(new_block)) ())  # this works now
    
    # this also works
    #new_args.append(quote(break))
    #new_block = Block(new_args)
    #return quote(while(true, unquote(new_block)))


    #return quote((lambda[ref] (unquote(new_block)): void) ())  # this doesn't work, 'Unexpected typed call' ?

    # this works but be careful to mark as void or return nothing
    # new_args.append(quote(return))
    #call_args: [Node] = [new_block]
    #l = Call(quote(lambda[ref]), call_args)
    #return quote(unquote(l)())
)


def (main:
    with_newlines (:
        std.cout << "Hello"
        std.cout << "World"
    )
)
