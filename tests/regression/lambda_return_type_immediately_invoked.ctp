
def (main:
    val = lambda(x:
        x
    ):int (5)
    std.cout << val
    val2 = lambda(x:
        # "hi".c_str()  # nice silent ub (aside: cout is not a safe interface)
        c"hi"
    ):const:char:ptr(5)
    std.cout << val2
)
    