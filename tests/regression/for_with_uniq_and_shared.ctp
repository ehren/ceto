unsafe.extern(printf, static_cast)

class (Uniq:
    x = 0

    def (bar: mut:
        self.x = self.x + 1
        printf("in bar %d %p\n", self.x, static_cast<const:void:pointer>(this))
        return self.x
        unsafe (:
            # just ensure the manual approach compiles too (unreachable):
            this->x = this->x + 1
            printf("in bar %d %p\n", this->x, static_cast<const:void:pointer>(this))
            return this->x
        )
    )
): unique

class (Shared:
    x = 0

    def (foo:
        printf("foo\n")
        return 10
    )
)

class (Shared2:
    x
)

def (main:
    x = 5
    for (x:mut:auto:ref:ref in [1, 2, 3]:
        # TODO iterating over a square bracket ListLiteral should allow an explicit ref iter var
        unsafe(:
            printf("%d\n", x)
            x = x + 1
        )
    )
    
    static_assert(std.is_const_v<decltype(x)>)

    # TODO these two loops would use const:auto:ref (and a range based for) because lst is a (non-aliased) local val.
    # we should allow an explicit ref type here too

    lst : mut = [1,2,3]
    for (x:mut:auto:ref:ref in lst:
        unsafe (:
            printf("%d\n", x)
            x = x + 1
        )
    )
    for (x:mut:auto:ref:ref in lst:
        unsafe(:
            printf("%d\n", x)
            x = x + 1
        )
    )
    
    u : mut = []
    s : mut = []
    s2 : mut = []
    for (x in [1, 2, 3, 4, 5]:
        u.append(Uniq() : mut)
        s.append(Shared())
        s2.append(Shared2("blah"s))
    )
    
    for (x:mut:auto:ref in u:
        printf("%d\n", unsafe(x->bar()))
        printf("%d\n", unsafe(x).bar())
        # zz = x # correct error
    ) : unsafe
    
    n : mut:int = 0
    for (x:mut:auto:ref in u:
        printf("bar again: %d\n", x.bar())
        # zz = x # correct error
        # x = Uniq()
        n = n + 1
        if (n % 2 == 0:
            x.bar()
        )
    ): unsafe
    for (x:mut:auto:ref in u:
        printf("bar again again: %d\n", x.bar())
        # zz = x # correct error
        # x = Uniq()
    ): unsafe
    
    # v = [] #fix decltype(i)
    v : mut = [Shared() : mut]
    v2 : mut = [Shared()]
    
    for (i in s:
        i.foo()
        # n = i
        # v.append(i)  # error (i is const v contains mut elems)
        v2.append(i) # v2 is not const, contains const elemens
    )
    
    for (vv2 in v2:
        vv2.foo()
    )
    
    s1 = Shared() : mut

    # needs mut iter var because propagate_const
    for (v1:mut:auto in v:
        v1.x = 55
        
        std.cout << "v:" << v1.foo()
        # v1 = s1
    )
)
    
