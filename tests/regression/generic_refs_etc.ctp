
    
# def (foo, x: auto: ref:  #  error: 'auto' not allowed in function prototype
# def (foo, x: ref:  # should work (stay in template generation mode)
def (foo, x:
    return x
)
    
def (main:
    x = 1
    xref:auto:ref = x # TODO auto inject auto in the local var case
    y: const : auto = 2 
    z : const : auto : ref = 3
    # w : const : ref : auto = 4#   const & auto w = 4;   # not valid c++ syntax
    
    r : const : int : ref = xref
    r2 : int : const : ref = xref
    # r : ref = xref
    
    # p : ptr = 0 # generating "*p = 0;" is bad
    p:const:auto:ptr = &x
    p2: const:auto:ptr:ptr = &p
    p3: int:const:ptr = &x
    # p4 : const:ptr:int = &x #  const * int p4 = (&x);  error expected unqualifief id
    
    
    # These are all bad ideas (we don't / no plans to support these 'conveniences')  (ptr and ref will eventually
    # w1 : ref = x # really auto:ref
    # w2 : const:ref = x # const:auto:ref
    # w3 : ptr = &x # auto:ptr
    # w4 : const:ptr = &x # const:auto:ptr
    
    # rules:  # have to look at outer expression node...
    # see ptr - output auto*
    # see const:ptr - output const auto* 
    
    foo(1)
)
    