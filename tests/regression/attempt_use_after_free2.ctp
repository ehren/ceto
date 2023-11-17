# Test Output: in Foo: 1
# Test Output: in Foo: 2
# Test Output: in Foo: 3
# Test Output: Foo destruct
# Test Output: in Foo: 4
# Test Output: in Foo: 5
# Test Output: ub has occured

# no plans to address - be careful with multithreaded code!

include <chrono>

class (Foo:
    x : int = 1

    def (long_running_method: mut:
        while (x <= 5:
            std.cout << "in Foo: " << self.x << "\n"
            std.this_thread.sleep_for(std.chrono.seconds(1))
            self.x += 1
        )
    )

    def (destruct:
        std.cout << "Foo destruct\n"
    )
)

class (Holder:
    f : Foo:mut = None
    
    def (getter:
        return f
    )
)

def (main:
    g = Holder() : mut
    g.f = Foo() : mut
    
    t: mut = std.thread(lambda(:
        # g.getter().long_running_method()  # this "works" (getter returns by value ie +1 refcount) although still a race condition plus UB due to no atomics
        g.f.long_running_method()  # this is a definite use after free
    ))
    
    std.this_thread.sleep_for(std.chrono.milliseconds(2500))
    g.f = None
    
    t.join()
    
    std.cout << "ub has occured\n"
)
    