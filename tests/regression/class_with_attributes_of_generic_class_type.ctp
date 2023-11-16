# Test Output: 3001
# Test Output: 12123
# Test Output: hi2234
# Test Output: e2

class (Foo:
    a
    b
    c
) 

class (Bar:
    a
    b
    # f : Foo  # probably need to forget about this # indeed we have
    f : Foo<decltype(a), decltype(b), decltype(b)>
)

class (Bar2:
    a
    b
    f : decltype(Foo(b,b,b))  # this is probably more intuitive than explicit template syntax although produces wackier looking but equivalent c++ code (either way both cases work)
)

class (MixedGenericConcrete:
    a
    b : int
)

# class (GenericList:
#     lst : [decltype(x)]   # this kind of thing won't work without a forward declaration somewhere

#     def (init, x...:  # need syntax for template varargs
#         self.lst = *x # need different syntax than python !! or do we
#         self.lst = x... # maybe
#     )
#     
# )
# or instead
# class (GenericList:
#     lst : []   # implicit typename T1, std::vector<T1>() 
#     dct : {}   # implicit typename T2, typename T3, std::unordered_map<T2, T3> {}
# )
# but then need explicit template instantiation to invoke...

def (main:
    f = Foo(1,2,3)
    f2 = Foo(1,2,[3])
    # f3 = Foo(1,2,[])
    # f3.c.append(1)
    f4 = Foo(1, 2, Foo(1, 2, 3))
    f5 = Foo(1, 2, Foo(1, Foo(1, 2, Foo(1,2,3001)), Foo(1,2,3)))
    std.cout << f5.c.b.c.c << "\n"
    b = Bar(1, 2, f)
    std.cout << b.a << b.b << b.f.a << b.f.b << b.f.c << "\n"
    b2 = Bar2("hi", 2, Foo(2,3,4))  # should work
    std.cout << b2.a << b2.b << b2.f.a << b2.f.b << b2.f.c << "\n"
    m = MixedGenericConcrete("e", 2)
    std.cout << m.a << m.b << "\n"
)

class (HasGenericList:
    # a : [] #?
    # needed if want
    # h = HasGenericList()
    # h.a.append(1)
    # is it really useful? (when the `append` must occur in same scope as construction)
    
    pass # FIXME: shouldn't create attribute named pass.
)

        