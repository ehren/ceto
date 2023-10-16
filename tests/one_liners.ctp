
def (main, argc:int, argv:char:ptr:ptr:
    # if ((1:int): printf("1") : some_type_lol elif 2 == 4: printf("2") else: printf("3") )
    # if (1:int: printf("1") : some_type_lol elif 2 == 4: printf("2") else: printf("3") )   # warning: declaration does not declare anything:  int;
    # ^ we no longer discard types on non-assignment expressions (now printed as var declarations)
    
    # with '=' lower precedence than ':'
    if ((x = 5): printf("%d", x), elif: argc == 1: printf("1"), elif: (y = 5): printf("unreachable %d", y), else: (z = 10))
)
    