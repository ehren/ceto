
class (Foo:
    def (destruct:
        std.cout << "Foo destruct"
    )
)

def (aliaser, f : mut:auto:ref, g:
    std.cout << "in aliaser"
    f = nullptr
    std.cout << (&g)->use_count()  # 0
    std.cout << ((&g)->get() == nullptr)  # 1
    std.cout << (g == nullptr)  # 1
)

def (main:
    f : mut = Foo()
    aliaser(f, f)
)
    