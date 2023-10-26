

class (Bar:
    a
)
    
class (Foo:
    a : std.atomic<int> = 0
    go : std.atomic<bool> = true
    go2 : std.atomic<bool> = std.atomic<bool> {true}  # this shouldn't be / isn't necessary
)

def (main:
    f : mut = Foo()

    t : mut = std.thread(lambda(:
        while (f.a < 100000:
            std.cout << f.a << "\n"
        )
        f.go = false
    ))

    t2 : mut = std.thread(lambda(:
        while (f.go:
            f.a = f.a + 1   # took us a while to implement += etc
            f.a.operator("++")()  # alternative
            f.a.operator("++")(1) 
            f.a += 1  # += now implemented
        )
    ))

    t.join()
    t2.join()
)

    