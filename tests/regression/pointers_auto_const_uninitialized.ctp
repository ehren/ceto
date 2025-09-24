

def (main:
    val : mut:int
    val_east : int:mut
    unsafe (:
        a : int:pointer = &val  # a is const (not what it's pointing to); this is fine (roughly the behavior as if we had applied add_const_t to everything)
        a2 : int:pointer = &val_east
        *a = 5
        *a2 = 5
        # a = nullptr   # error
        # a2 = nullptr  # error
    )
)
        
