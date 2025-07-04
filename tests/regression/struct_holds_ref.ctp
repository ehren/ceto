# Test Output: 155155

defmacro (struct_and_class(args), args: [Node]:
    id = args[0]

    # TODO splice would make this easier
    new_args: mut = args

    new_args[0] = Identifier(id.name().value() + "_class")
    clazz = Call(Identifier("class"), new_args)  

    new_args[0] = Identifier(id.name().value() + "_struct")
    strct = Call(Identifier("struct"), new_args)

    # somewhat of a hack to replace a single call with 2 calls at file scope:
    return quote(if (1:
        unquote(clazz)
        unquote(strct)
    ): preprocessor)
)

struct (Foo:
    x: int
)

struct_and_class (HoldsFooConstRef:
    foo: const:Foo:ref
)

# TODO should be:
# struct_and_class (HoldsFooConstRef:
#    foo: unsafe:const:Foo:ref
# ): unsafe(safe=True)  # alternately HoldsFooConstRef should be restricted to unsafe blocks

struct_and_class (HoldsFooMutRef:
    foo: Foo:ref

    def (uses_field:

        blah: const:auto:ref = 5
        unsafe (:
            # both locals and fields of ref type (even if const) require an unsafe block
            std.cout << blah << self.foo.x
        )
    )
)

def (main:
    scope(:
        foo = Foo(1)
        foomut: mut = Foo(2)
        h = HoldsFooConstRef_class(foo)
        h2 = HoldsFooConstRef_class(foomut)
        #hm = HoldsFooMutRef_class(foo)  # error
        #hm: mut = HoldsFooMutRef_class(foo)  # error
        hm = HoldsFooMutRef_class(foomut)
        #h.foo.x = 5  # error
        #h2.foo.x = 5  # error
        hm.foo.x = 5
        std.cout << h.foo.x
        std.cout << foomut.x
        std.cout << h2.foo.x
    )
    scope(:
        foo = Foo(1)
        foomut: mut = Foo(2)
        h = HoldsFooConstRef_struct(foo)
        h2 = HoldsFooConstRef_struct(foomut)
        #hm = HoldsFooMutRef_struct(foo)  # error
        #hm: mut = HoldsFooMutRef_struct(foo)  # error
        hm = HoldsFooMutRef_struct(foomut)
        #h.foo.x = 5  # error
        #h2.foo.x = 5  # error
        hm.foo.x = 5
        std.cout << h.foo.x
        std.cout << foomut.x
        std.cout << h2.foo.x
    )
)
