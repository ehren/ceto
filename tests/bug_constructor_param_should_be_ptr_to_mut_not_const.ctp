# Test Output: 0

class (Node:
    func : Node:mut
    args : [Node:mut]

    def (init,
         func,  # this was incorrectly codegening as const shared_ptr<const Node>& rather than const shared_ptr<Node>&
         args:
        self.func = func
        self.args = args
        static_assert(std.is_reference_v<decltype(func)>)
        static_assert(std.is_const_v<std.remove_reference_t<decltype(func)>>)
        static_assert(not std.is_const_v<decltype(self.func)>)
    )
)

def (main:
    std.cout << Node(nullptr, [] : Node:mut).args.size()
)
    