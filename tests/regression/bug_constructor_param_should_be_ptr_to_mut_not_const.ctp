# Test Output: 0

class (Node:
    func : Node:mut
    args : [Node:mut]

    def (init,
         func,
         args:
        self.func = func
        self.args = args
        # func must be passed by value because of Node:mut w/ propagate_const
        # note this test will break when we auto std.move the last use of anything passed by non-const value (not just :unique)
        static_assert(not std.is_reference_v<decltype(func)>)
        static_assert(not std.is_const_v<std.remove_reference_t<decltype(func)>>)
        static_assert(not std.is_const_v<decltype(self.func)>)
    )
)

def (main:
    std.cout << Node(nullptr, [] : Node:mut).args.size()
)
    
