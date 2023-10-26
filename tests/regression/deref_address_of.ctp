
    
class (Blah:
    def (huh:
        std.cout << "huh" << "\n"
    )
)

# def (hmm, x: int:ref:const:
#     pass
# )
    
def (main:
    Blah().huh()
    b = Blah()
    b.huh()  # auto unwrap via template magic
    b->huh() # no magic (but bad style for object derived class instances!)
    printf("addr %p\n", static_cast<const:void:ptr>((&b)->get())) # cheat the template magic to get the real shared_ptr (or rather a pointer to it)
    # printf("addr %p\n", (&b).get()) # woo hoo this no longer works! (we previously autoderefed _every_ pointer on every attribute access...)
    # printf("addr temp %p\n", (&Blah())->get())  #  error: taking the address of a temporary object of type 'typename enable_if<!is_array<Blah> ... - good error
    # printf("use_count %ld\n", (&b).use_count())  # no autoderef for arbitrary pointers!
    printf("use_count %ld\n", (&b)->use_count())
    b_addr = &b
    printf("addr of shared_ptr instance %p\n", static_cast<const:void:ptr>(b_addr))
    # printf("addr %p\n", b_addr.get()) # correct error
    printf("addr %p\n", static_cast<const:void:ptr>(b_addr->get()))
    # printf("use_count %ld\n", b_addr.use_count()) # correct error
    printf("use_count %ld\n", b_addr->use_count())
    (*b_addr).huh() # note *b_addr is a shared_ptr<Blah> so accessing via '.' already does deref magic (it's fine)
    (*b_addr)->huh()   # no deref magic is performed here (though arguably bad style)
)
    