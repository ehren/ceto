
def (main:
    # x : const:auto:ref = 1
    # y : int:ref = x  # no mut so const by default
    # static_assert(std::is_const_v<decltype(x)>)
    # static_assert(std::is_const_v<decltype(y)>)
    
    x:int = 0
    r2 : int : const : ref = x
    y : int:ref = x  # no mut so const by default
)
    