
def (main:
    x : mut = []  # this should not be captured (that is, make sure the def of 'x' in 'x + y' points to the lambda arg 'x' and not the list 'x')
    lfunc = lambda (x, y, x + y)
    x.append(1)
    std.cout << lfunc(x[0], x[0])
)
    