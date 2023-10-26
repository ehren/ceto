

class (C:
    a:int
)
    
def (foo, c: C:
    pass
)

def (bar, c: const:C:
    pass
)

def (byval, c: std.type_identity_t<C>:   # not literal "C" or "const:C"/"C:const"  - ordinary function local rules apply: C simply shared_ptr<C>
    # this only holds for the circumstances in this test (byval called with a temporary should have use_count() == 1)
    assert ((&c)->use_count() > 1)
    
    # writing C:: or C. now results in just "C" not shared_ptr<C>:
    # static_assert(std.is_same_v<std.shared_ptr<C::element_type>, decltype(c)>)  # not portable ceto code of course
    # ^ so this sort of wonky stuff needs to be rewritten:
    
    # we currently print C (not in a scope resolution or attribute access context) as shared_ptr<C>
    # so this is probably the most canonical way to get at the real class (still not "portable" of course):
    static_assert(std.is_same_v<const:std.shared_ptr<std.type_identity_t<C>::element_type>, decltype(c)>)
    
    # other similar "non-portable" (imaging a non-C++ backend) code:
    # static_assert(std.is_same_v<std.shared_ptr<decltype(*c)>, decltype(c)>)  # TODO this fails because an UnOp is always overparenthesized due to current naive use of pyparsing.infix_expression (e.g. (*p).foo() is parsed correctly precedence-wise but need for parenthesese in code printing discarded or rather handled by overparenthesizing all UnOps in every context) - leading to use of overparenthesized decltype((*p)) in c++. "workaround" for now is:
    static_assert(std.is_same_v<const:std.shared_ptr<std.remove_reference_t<decltype(*c)>>, decltype(c)>)
)

def (byconstref, c: C:
    # this only holds for the circumstances in this test
    assert ((&c)->use_count() == 1)
    
    static_assert(std.is_reference_v<decltype(c)>)
)

def (main:
    c = C(1)
    foo(c)    
    bar(C(1))    # implicit conversion
    bar(c)       # implicit conversion
    
    c2 : const:C = C(2)  # implicit conversion
    c3 : const:C = c     # implicit conversion
    bar(c2)
    bar(c3)
    # foo(c2)            # error no matching function
    
    # c = c3             # error (no known conversion from shared const to non-const)
    # cmut : C = c3      # same
    
    # TODO
    # cc = C() : const  # cc is const shared_ptr<const C>
    
    c4 = C(1)
    byval(c4)
    byconstref(c4)
)
    