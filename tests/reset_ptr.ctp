
class (Foo:
    # x = 0  # this is now const by default
    x : int = 0  # TODO this should be too

    def (bar:
        printf("bar %d\n", self.x)
    )
    
    def (destruct:
        printf("dead\n")
    )
    
    def (operator("=="), other: Foo:
        printf("in == method - both foo\n")
        return self.x == other.x
    )
    def (operator("=="), other:
        printf("in == method - other not foo\n")
        return other == 5
    )
)

def (operator("=="), f: Foo, other:
    return f.operator("==")(other)
)
def (operator("=="), f: Foo, otherfoo: Foo:
    return f.operator("==")(otherfoo)
)

def (operator("=="), f: Foo, other: std.nullptr_t:   # "fix" (?) use of overloaded operator '==' is ambiguous
    return not f
    #return f.operator("==")(other)
    #return nullptr == f   # this is no longer possible in c++20 due to the symmetric binary operator reversing scheme (though clang++ on linux seems to accept it)
)

def (main:
    # f:mut = Foo()  # regardless of the reset case below, getting the above overloading to work for mut case is now problematic after 'func params const by default' (probably this whole approach of overriding free standing func operators on the shared_ptrs is problematic)
    f = Foo()
    f.bar()
    if (f == 5:
        printf("overload == works\n")
    )
    # b:mut = Foo()
    b = Foo()
    if (f == b:
        printf("same\n")
    else:
        printf("not same\n")
    )
    # f = nullptr
    # b = nullptr
    f2 : Foo = nullptr
    printf("testing for null...\n")
    if (f2 == nullptr:
        printf("we're dead\n")
    )
    
    if (not f2:
        printf("we're dead\n")
    )
)
    