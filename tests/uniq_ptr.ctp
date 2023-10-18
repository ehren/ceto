# Test Output: bar 5
# Test Output: bar 5
# Test Output: bar 5
# Test Output: bar 5
# Test Output: bar 5
# Test Output: bar 5
# Test Output: bar 5
# Test Output: bar 5
# Test Output: bar 5


class (Foo:
    a:int = 5
    
    def (bar:
        printf("bar %d\n", self.a)
        return self.a
    )
): unique

def (bam, f: Foo:
    f.bar()
)

def (baz, f: Foo:
    f.bar()
    bam(f)  # last use automoved
)

def (main:
    Foo().bar()
    
    baz(Foo())

    f : mut = Foo()
    f.bar()

    f2 : mut = Foo()
    f2.bar()

    # baz(std.move(f2))  # this is no longer necessary
    baz(f2)  # automatic move from last use

    # lst = [Foo(), Foo(), Foo()]  # pfft https://stackoverflow.com/questions/46737054/vectorunique-ptra-using-initialization-list
    lst : mut = []
    lst.append(Foo() : mut)
    f = Foo() : mut
    # lst.append(std.move(f))  # no longer necessary
    lst.append(f)

    lst[0].bar()
    lst[1].bar()
)
    