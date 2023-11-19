def (main:
    x = 1
    # xref: auto:ref = x  # error must specify mut/const
    xref: const:auto:ref = x
    y: const:auto = 2
    z: const:auto:ref = 3

    r: const:int:ref = xref
    r2: int:const:ref = xref
    # r : ref = xref
    
    # p : ptr = 0 # error (we avoid generating "*p = 0;" !!)
    p: const:auto:ptr = &x
    p2: const:auto:ptr:ptr = &p
    p3: int:const:ptr = &x
    # p4 : const:ptr:int = &x #  const * int p4 = (&x);  error expected unqualifief id
    
)
    