
    
def (main:
    val : mut:int
    a : int:ptr = &val  # a is const (not what it's pointing to)
    a = nullptr  # error
)
    