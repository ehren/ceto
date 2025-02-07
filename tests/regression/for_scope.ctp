
def (main:
    x = 5
    
    l : mut = [1,2,3]
    for (x:mut:auto:rref in l:
        x = x + 1
    )
    
    for (x in l:
        unsafe(printf("%d", x))
    )
    
    for ((x:mut:auto:rref) in [1, 2, 3]:
        x = x + 1
        unsafe(:
            printf("%d", x)
        )
    )
        
    unsafe(printf("%d", x))
)
