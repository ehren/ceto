
    
class (Foo:
    def (blah:static:
        std.cout << "blah"
    )
)
    
def (main:
    # note different precedence of these two expressions (not sure if 'print some AttributeAccess instances with ::' needs to be more robust ie include post parse ast fixups - it will be required if we want call_or_construct wrapper for namespace resolved ceto class constructor calls e.g. f = mymodule.Foo())
    Foo::blah()
    Foo.blah()  # template metaprogramming solution to treat as scope resolution if Foo is a type, attribute access otherwise? (would be ugly if possible? would require forwarding).
    
    # note this Call node is currently not wrapped in call_or_construct (this will have to change when a module/import system is implemented):
    std.cout << std::vector(500, 5).at(499) << std::endl
    
    std::vector : using
    
    # note: using declarations aren't taken into account by safe lookup rules (good! should just ban them or require unsafe.extern(using))
    unsafe.extern(vector)
    v = vector(500, 5)  # ensure vector survives current 'call_or_construct' handling (later note: call_or_construct is no longer used - interferes with e.g ctad lst = [Foo{1)])
    std.cout << v.at(499)
)
    
