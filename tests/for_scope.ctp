
def (main:
    x = 5
    
    l : mut = [1,2,3]
    for (x:mut:auto:rref in l:  # note the context sensitivity disguised by a post parse fixup (ordinarily ':' has a lower precedence than 'in')
        x = x + 1
    )
    
    for (x in l:
        printf("%d", x)
    )
    
    for ((x:mut:auto:rref) in [1, 2, 3]:
        x = x + 1
        printf("%d", x)
    )
        
    printf("%d", x)
)
    