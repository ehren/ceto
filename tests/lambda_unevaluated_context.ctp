
    
# handling of globals may change in future e.g. automatic constexpr
# test tries to ensure the below class scope lambdas not printed with a capture list
# although detecting decltype/subtype usage still necessary
g:int = 5

class (Foo:
    
    # our current 'is void lambda return?' and 'diy non-narrowing init' checks make the codegen for this typed assignment a bit large (it's fine)
    a : int = lambda(5 + g)()
    
    f : std.conditional_t<false, decltype(lambda(x, x + g)), int>
)

cg = "it's a global, no need to capture"c  # (and you can't because a const:char:ptr is not a shared_ptr<object> or is_arithmetic_v)

def (main:
    f = Foo(2)
    l = lambda (g + f.a)  # capture list for 'f' works here, g has a GlobalVariableDefinition so is not captured
    l2 = lambda (cg)  # ensure we _don't_ capture a global (this ensures this access is an ordinary c++ read of a global rather than an attempted capture that would fail the ceto::default_capture check).
    std.cout << f.f << f.a << l() << "\n" << l2()
)

    