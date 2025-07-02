# Test Output: in Foo: 1
# Test Output: in Foo: 2
# Test Output: in Foo: 3
# Test Output: Foo destruct
# Test Output: in Foo: 4
# Test Output: in Foo: 5
# Test Output: ub has occured

# be careful with multithreaded code! (std.thread iS unSaFe)

include <chrono>

class (Foo:
    x : int = 1

    def (long_running_method: mut:
        while (self.x <= 5:
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
        return self.f
    )
)

def (main:
    g: mut = Holder()
    g.f = Foo() : mut

    t: mut = std.thread(lambda(:
        gm: mut = g  # capture is const so we can't mutate through g (because of copyable propage_const), but we can mutate through a mut copy:
        #gm.getter().long_running_method()  # this would be fine - we copy capture g/gm by value and getter returns a fresh shared_ptr instance bumping refcount (different threads accessing different shared_ptr instances even if pointing to same thing is thread safe)
        gm.f.long_running_method()  # accessing 'gm' (different shared_ptr instances due to implicit copy capture) is safe. accessing the same shared_ptr instance 'f' is UB and a reliable use after free on all 3 platforms
    ))

    std.this_thread.sleep_for(std.chrono.milliseconds(2500))
    g.f = None

    t.join()

    std.cout << "ub has occured\n"
)

