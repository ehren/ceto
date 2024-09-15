include <iostream>

def (main:
    scope(:
        x: int = 5
        std.cout << x
    )
    x: float = 5.0
    std.cout << x
)
