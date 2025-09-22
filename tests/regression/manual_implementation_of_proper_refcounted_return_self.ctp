unsafe.extern(std.static_pointer_cast, shared_from_this, ceto.get_underlying)
    
class (A:
    a
)

# note that this approach needs adjustments for template classes (codegen now correctly handles 'self' even in template case via ceto::shared_from)
class (S:
    def (foo:
        # note that S:: or S. is treated as static attribute access of the c++ class S (fool transpiler by inserting std.type_identity_t so that S as an identifier's parent is not an instance of ScopeResolution/AttributeAccess):
        return std.static_pointer_cast<std.type_identity_t<S>::element_type>(shared_from_this())
    )
    
    def (foo2:
        # alternately
        return std.static_pointer_cast<std.remove_reference<decltype(*this)>::type>(shared_from_this())
        
        # no need for overparenthization any more (debatable if we need to parse this now that other template parse improvements have been made)
        return (std.static_pointer_cast<std.remove_reference<decltype(*this)>::type>)(shared_from_this())
    ) : S  # <strike>no need for return type (but S correctly handled as shared_ptr<S> here)</strike>
           # now that propagate_const introduced the explicit return type correctly wraps the instance in propagate_const. foo() is incorrectly not wrapped in prop_const (s2 below doesn't require ceto.get_underlying)
)

def (main:
    s = S()
    std.cout << (&ceto.get_underlying(s))->use_count() << std.endl
    s2 = s.foo()
    std.cout << (&s2)->use_count() << std.endl
    a = A(s)
    std.cout << (&s2)->use_count() << std.endl
    s3 = a.a.foo2()
    std.cout << (&ceto.get_underlying(s))->use_count() << std.endl
    std.cout << (&(ceto.get_underlying(s3)))->use_count() << std.endl
    
    # no: dyncast(B, a)
    # no: staticcast(B, a)  # not a good idea to make static_pointer_cast convenient
    # isinstance(a, B)
    # asinstance(a, B)   # std::dynamic_pointer_cast<B>(a)  # maybe this is better than 'dyncast'
    # ^ isinstance/asinstance now implemented
)
    
    
