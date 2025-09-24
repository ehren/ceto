unsafe.extern(printf)

class (Blah:
    def (foo:
        printf("in foo method\n")
    )
)

def (main:
    a = Blah()
    b = Blah()
    l: [Blah] = [a, b]
    l[1].foo()
    
    s: [std.string] = ['a', 'b', 'c']
    unsafe (:
        # can't pass s[0][0] maybe by ref with other non-simple params outside of unsafe
        printf('%s is the last element. %c is the first.\n', s[2].c_str(), s[0][0])
    )
)
