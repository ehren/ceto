# Test Output 1
# Test Output 2
# Test Output 3
# Test Output 123123

# requires --_norefs

class (Foo:
    a = [1, 2, 3]

    def (bar:
        pass
    )

    def (foo:
        #for (x in self.a:  # static_assert this->a is_reference_v (same with self.a but self rewritten to this)
        #for (x in this->a: # same
        a = self.a
        for (x in a:
            std.cout << x # << std.endl  # static_assert std.cout << x is_reference_v
            std.cout << "\n"
            self.bar()  # may modify self.a but fine because we made a copy
        )

        l = lambda(:
            self.bar()
        )

        s = self

        # unsafe:mut:auto:ref:ref in the future!
        b: mut:auto:ref:ref = self.a
        for (x in b:
            std.cout << x
            # b  # error - direct use of iterable
            self.bar()  # even if bar was mut (may modify self.a) this would still be allowed (due to potentially propagating unsoundness of unsafe:mut:ref)
            l()
            s.bar()
        )

        for (x in self.a:
            std.cout << x
            # b  # error
            # self.bar()  # error. TODO we can add more logic allowing this known const (because foo const) method call
            # l() # error
            # s  # error
        )
    )
)

def (main:
    f = Foo()
    f.foo()
)
