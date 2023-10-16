
class (Foo:
    pass
)
    
def (main:
    # both fine:
    if (Foo():mut:
        std.cout << 5
    )    
    if ((Foo():mut):
        std.cout << 5
    )
    
    # TODO mut/const calls aren't handled in the post parse one liner if expander (allowing shared/unique/etc in more places e.g. FooStruct:shared as an easier way to write shared_ptr<const FooStruct> will cause similar problems)
    # if (Foo():mut: std.cout << 5)  # ceto.codegen.CodeGenError: ('unexpected type', (std.cout << 5)) # if statement from one_liner_expander has a Block with 1 statement 'mut:std.cout << 5'
    if ((Foo():mut): std.cout << 5)  # acceptable workaround for now
)
    