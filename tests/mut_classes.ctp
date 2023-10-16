
    
class (Blah:
    x #: mut  # error unexpected placement of 'mut' (good error: const data members by default or otherwise are bad - prevents move optimizations + other wacky issues)
    def (foo:mut:
        self.x = self.x + 1
    )
)

def (main:
    b : mut = Blah(1)
    b.foo()
    std.cout << b.x
    b.x = 5
    std.cout << b.x
)

    