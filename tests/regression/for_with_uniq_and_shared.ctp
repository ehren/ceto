

class (Uniq:
    x = 0

    def (bar: mut:
        self.x = self.x + 1
        printf("in bar %d %p\n", self.x, static_cast<const:void:ptr>(this))
        return self.x
        # just ensure the manual approach compiles too (unreachable):
        this->x = this->x + 1
        printf("in bar %d %p\n", this->x, static_cast<const:void:ptr>(this))
        return this->x
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
    for (x:mut:auto:rref in [1, 2, 3]:
        printf("%d\n", x)
        x = x + 1
    )
    
    static_assert(std.is_const_v<decltype(x)>)
    
    lst : mut = [1,2,3]
    for (x:mut:auto:rref in lst:
        printf("%d\n", x)
        x = x + 1
    )
    for (x:mut:auto:rref in lst:
        printf("%d\n", x)
        x = x + 1
    )
    
    u : mut = []
    s : mut = []
    s2 : mut = []
    for (x in [1, 2, 3, 4, 5]:
        u.append(Uniq() : mut)
        s.append(Shared())
        s2.append(Shared2("blah"s))
    )
    
    for (x in u:
        printf("%d\n", x->bar())  # should not be encouraged
        printf("%d\n", x.bar())
        # zz = x # correct error
    )
    
    n : mut:int = 0
    for (x in u:
        printf("bar again: %d\n", x.bar())
        # zz = x # correct error
        # x = Uniq()
        n = n + 1
        if (n % 2 == 0:
            x.bar()
        )
    )
    for (x in u:
        printf("bar again again: %d\n", x.bar())
        # zz = x # correct error
        # x = Uniq()
    )
    
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
    
    for (v1 in v:
        v1.x = 55
        
        std.cout << "v:" << v1.foo()
        # v1 = s1
    )
)
    
