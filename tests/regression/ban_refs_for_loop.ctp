# Test Output 1
# Test Output 2
# Test Output 3
# Test Output 1231234

# requires --_norefs
#

def (bad, a, b:mut:auto:ref:  # should be marked unsafe
    for (x in a:
        b.push_back(1337)
    )
)

def (bad2, a, b:mut:auto:ref:
    begin = a.cbegin()
    begin = unsafe(a.cbegin())
    end = a.cend()
    b.clear()
    std.cout << std.find(begin, end, 1) != end
)

class (Foo:
    a = [1, 2, 3]


    def (mm: mut:
        pass
    )

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

    def (foo: mut:
        self.a.push_back(4)

        #std.cout << self.a[3]

        std.cout << (std.find(self.a.begin(), self.a.end(), 1) != self.a.end())
    )
)

class (Blah:
    foo: Foo:mut = Foo()
)

def (main:
    f = Foo()
    f.foo()

    m: mut = Foo()
    m.foo()
    # std.cout << m.a[3] # error
    # element = m.a[3] # error
    ma = m.a
    element = ma[3]
    std.cout << element

    for (x in m.a:
        #ma2 = m.a
        ma2 = ma
        std.cout << x
    )

    ma3: mut = m.a
    bad(ma3, ma3)

    b = Blah()

    #b.foo.mm()

)
