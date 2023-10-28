
def (main:
    std.cout << "\t\f\n"  # TODO transpiler shouldn't be expanding \t and \f plus similar probs
    std.cout << std.endl << "\"" << std.endl
    std.cout << '"' << std.endl
    std.cout << '\"'  << std.endl  # Note that in python '\"' is the same as '"'
    std.cout << '\\"' << std.endl
    std.cout << '\\\"' << std.endl  # in python '\\\"' == '\\"' (same for us) ? likely dubious
)