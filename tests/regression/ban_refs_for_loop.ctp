# Test Output 1
# Test Output 2
# Test Output 3
# Test Output 123

# requires --_norefs

class (Foo:
    a = [1, 2, 3]

    def (foo:
        #for (x in self.a:  # static_assert this->a is_reference_v (same with self.a but self rewritten to this)
        #for (x in this->a: # same
        a = self.a
        for (x in a:
            std.cout << x # << std.endl  # static_assert std.cout << x is_reference_v
            std.cout << "\n"
        )
        # unsafe:mut:auto:ref:ref in the future!
        b: mut:auto:ref:ref = self.a
        for (x in b:
            std.cout << x
        )
    )
)

def (main:
    f = Foo()
    f.foo()
)
