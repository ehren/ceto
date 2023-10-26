
class (Blah:
    def (foo:
        printf("in foo method\n")
    )
)

def (main:
    a = Blah()
    b = Blah()
    l = [a, b] : Blah
    l[1].foo()
    
    s = ['a', 'b', 'c'] : string
    printf('%s is the last element. %c is the first.\n', s[2].c_str(), s[0][0])
    # print("hello", "world")
)
    