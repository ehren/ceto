# Test Output: in Foo: 1
# Test Output: in Foo: 2
# Test Output: in Foo: 3
# Test Output: Foo destruct
# Test Output: in Foo: 4
# Test Output: in Foo: 5
# Test Output: ub has occured

include <thread>
include <chrono>

unsafe.extern(std.thread, std.this_thread)

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
        gm: mut = g
        #gm.getter().long_running_method()  # this is probably still technically a race condition
        gm.f.long_running_method()  # accessing the same shared_ptr instance 'f' across two threads is definitely UB
    ))

    std.this_thread.sleep_for(std.chrono.milliseconds(2500))
    g.f = None

    t.join()

    std.cout << "ub has occured\n"
)

