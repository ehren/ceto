

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
        f_mut : mut = f
        while (f_mut.a < 100000:
            std.cout << f_mut.a << "\n"
        )
        f_mut.go = false
    ))

    t2 : mut = std.thread(lambda(:
        f_mut : mut = f
        while (f_mut.go:
            f_mut.a = f_mut.a + 1   # took us a while to implement += etc
            f_mut.a.operator("++")()  # alternative
            f_mut.a.operator("++")(1) 
            f_mut.a += 1  # += now implemented
        )
    ))

    t.join()
    t2.join()
)

    
