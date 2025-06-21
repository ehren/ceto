# Test Output: 1
# Test Output: 1

# TODO test harness has no "# Build Output: blah" comment mechanism

defmacro (node, node:
    std.cout << "found node:" << node.repr() << "\n"
    if (node.args.size() > 0 and node.args[0].name() == "main":
        std.cout << "skipping traversal of child nodes\n"
        return ceto.macros.Skip()
    )
    return node
)

defmacro(x << y, x, y:  # all logged by first macro
    if (y.equals(quote(std.endl)):
        return None  # avoid (infinitely) double adding std.endl
    )
    return quote(unquote(x) << unquote(y) << std.endl)
)

x = 1  # logged by macro

def (main:  # logged by macro but body skipped (due to Skip)
    # these won't be logged separately by the macro
    # (but they will get an extra std.endl from the other macro):
    std.cout << x
    std.cout << x
)

static_assert( # logged by macro
    true  # separately logged by macro
)
