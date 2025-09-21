# Example Output: 1
# Example Output: -529464832
# Example Output: -488570880
# Example Output: -520011712
# Example Output: -520011712
# Example Output: 11

struct (HoldsRef:
    x: int:ref
)

struct (Foo:
    vec: [int]

    def (foo: mut, x:
        # this could cause a vector relocation, invalidating references:
        for (i in std.ranges.iota_view(0, std.ssize(self.vec)):
            self.vec.append(i)
        )
        std.cout << x << std.endl
    )

    def (good: mut:
        # self.foo(vec[0])  # static_assert failure
        val = self.vec[0]
        self.foo(val)
    )

    def (bad: mut:

        self.foo(unsafe(self.vec[0]))  # UB

        r: mut:auto:ref = self.vec[0]
        self.foo(unsafe(r))  # why local ref vars are unsafe (UB)

        unsafe.extern(std.ref)
        
        self.foo(std.ref(self.vec[0]))  # UB

        self.foo(std.ref(unsafe(r)))  # UB

        # std.ref (like other unsafe.extern views and spans) is itself very dangerous
        std.cout << lambda(:
            x = 5
            return std.ref(x)
        ) ().get()  # UB

        # as are classes and structs that hold raw C++ references
        std.cout << lambda(:
            x: mut = 5
            # ceto defined classes/structs holding raw C++ refs can only be created in an unsafe context
            return unsafe(HoldsRef(x))
        ) ().x  # UB
    )
)

def (main:
    f: mut = Foo([1, 2, 3, 4])
    f.good()  # prints 1
    f.bad()   # UB (and reliably prints garbage)
)
