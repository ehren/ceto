# Test Output: 333123

class (Foo:
    a : [int]
    b : [int] = [1,2,3]
    c = [1,2,3] : int
    d = [1,2,3]
)
    
def (main:
    x:[int] = [1,2,3]
    l1 = [Foo(x)]
    lm : mut = []
    lm2 : mut = []
    lm3 : mut = []
    lm4 : mut = []
    lm5 : mut = []
    lm6 : mut = []
    lm8 : mut = []
    lm7 : mut = []
    lm9 : mut = []
    l2 = [Foo(x)] : Foo
    l3 : [Foo] = [Foo(x)]
    for (l in [l1, l2, l3]:
        lm.append(l[0].a[2])
        lm2.append(l3[0].a[2])
        a = l1[0].a[2]
        lm3.append(a)
        b = l[0].a[2]
        lm4.append(b)
        lm5.append(lm[0])
        lm6.append(lm2[0])
        lm7.append(l[0])
        lm8.append(lm7[0])
        c = l
        lm9.append(c[0])
    )
    
    std.cout << lm[0] << lm2[0] << lm4[0] << lm7[0].a[0] << lm8[0].b[1] << lm9[0].c[2]
)
    