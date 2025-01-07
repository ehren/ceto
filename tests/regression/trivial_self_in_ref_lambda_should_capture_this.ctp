
struct (Bar:
    x: int = 1
    def (bar:
        std.cout << lambda[ref](:
            return self.x
        )()
    )
)

def (main:
    Bar().bar()
)
