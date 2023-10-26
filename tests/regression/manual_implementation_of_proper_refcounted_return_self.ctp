
    
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
    ) : S  # no need for return type (but S correctly handled as shared_ptr<S> here)
)

def (main:
    s = S()
    std.cout << (&s)->use_count() << std.endl
    s2 = s.foo()
    std.cout << (&s2)->use_count() << std.endl
    a = A(s)
    std.cout << (&s2)->use_count() << std.endl
    s3 = a.a.foo2()
    std.cout << (&s)->use_count() << std.endl
    std.cout << (&s3)->use_count() << std.endl
    
    # dyncast(B, a)
    # staticcast(B, a)  # not a good idea to make static_pointer_cast convenient
    # isinstance(a, B)
    # asinstance(a, B)   # std::dynamic_pointer_cast<B>(a)  # maybe this is better than 'dyncast'
)
    
    