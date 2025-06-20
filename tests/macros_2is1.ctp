# Test Output: 1
# Test Output: 2
# Test Output: 4
# Test Output: 1

include <iostream>

defmacro (a, a: IntegerLiteral:
    if (a.integer_string == "2":
        return quote(1)
    )
    return None
)

defmacro(3:
    return quote(4)
)

defmacro(defmacro(args), args: [Node]:
    if ((block = asinstance(args.back(), Block)):
        if (isinstance(block.args[0], Call) and block.args[0].func.name() == "throw":
            # this is a defmacro whose first statement is a throw
            # it's probably trying to disable other defmacros (that's no fun)
            # silently disable it instead:
            return quote(static_assert(True))
        )
    )

    return None
)

# This macro will be disabled by the previous one.
# (note that if this macro was defined before the previous macro-disabling macro, 
#  the macro disabling macro itself would be an error)
defmacro(defmacro(args), args: [Node]:
    throw (std.logic_error("further macro definitions are banned"))
)

# macro disabling defmacros has been pre-emptively disabled (macros still ok)
defmacro(5:
    return quote(2)  # actually 1 given the above
)

defmacro(defmacro(args), args: [Node]:
    # our "disable macros disabling macros" macro fails to account for this case:
    std.cerr << "further macro definitions are banned (for real this time)\n"
    std.terminate()
)

# error: further macro definitions are banned (for real this time)
# defmacro(6:
#    return quote(5)
# )

def (main:
    std.cout << 2 << "\n"
    std.cout << 2 + 1 << "\n"
    std.cout << 3 << "\n" << 5 << "\n"
)
