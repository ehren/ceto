
def (main:
    if (1 & (&2):  # this would be rejected by the c++ compiler
        pass
    )
    if (1 && 2:    # but this raises a syntax error in the transpiler
        pass
    )
)
    