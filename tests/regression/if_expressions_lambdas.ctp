# Test Output: 122222222


def (main:
    x = if (1:
        [1, 2]
    else:
        [2, 1]
    )

    std.cout << x[0] << x[1]

    # halfway readable:
    result = lambda (x, if (x[1] == 2: x[1] else: x[0])) (x)  # note that the def of 'x' above uncovered a now fixed lambda capture bug (inappropriately capturing 'x' even though it's a lambda parameter)
    std.cout << if (result: result else: 0)

    # one liner if you insist
    std.cout << if ((r = lambda (x, if (x[1] == 2: x[1] else: x[0]))(x)): r else: 0)

    # multiline but single expression
    std.cout << if ((r = lambda (x:
        if (x[1] == 2:
            x[1]
        else:
            x[0]
        )
    ) (x)):
        r
    else:
        0
    )

    # no need for the lambda
    std.cout << if ((r = if (x[1] == 2:
        x[1]
    else:
        x[0]
    )):
        r
    else:
        0
    )

    # no need for the lambda - one-liner
    std.cout << if ((r = if (x[1] == 2: x[1] else: x[0])): r else: 0)

    # 'simple' nested expression if
    std.cout << if (if (x[1] == 2:
        x[1]
    else:
        x[0]
    ):
        x[1]
    else:
        0
    )

    # 'simple' nested expression if - one liner
    std.cout << if (if (x[1] == 2: x[1] else: x[0]): x[1] else: 0)
)

