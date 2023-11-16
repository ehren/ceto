# Test Output: aa0
# Test Output: generic node with func identifier node with name: a
# Test Output: (2 args.)
# Test Output: arg: identifier node with name: a
# Test Output: arg: identifier node with name: a
# Test Output: identifier node with name: a


class (Node:
    func : Node
    args : [Node]
    
    # TODO "overridable" / "canoverride" / "yesoverride"? otherwise "final" by default
    def (repr: virtual:
        r : mut = s"generic node with func " + if (self.func: self.func.repr() else: s"none") + "(" + std.to_string(self.args.size()) + " args.)\n"
        for (a in self.args:
            r = r + "arg: " + a.repr()
        )
        return r
    ) : string
    
    # TODO "overridable" implies virtual destructor
) : nonfinal

class (Identifier(Node):
    name : string
    
    def (repr:
        return s"identifier node with name: " + self.name + "\n"
    ) : string
    
    def (init, name:
        self.name = name
        # super.init(nullptr, std.vector<Node> {})  # this works but should't be required
        # super.init(nullptr, {})  # likewise - also not semantically identical (use of '{' and '}' nearly as dangerous as other c++ compat unsafe features)
        super.init(nullptr, [] : Node)  # nicer ceto solution
        # super.init(nullptr, [])  # transpiler error. TODO maybe just print "[]" as "{}" as a final fallback? only as a param?
    )
)

def (main:
    id = Identifier("a")
    std.cout << id.name
    id_node : Node = Identifier("a")  # TODO virtual destructor in Node if overridable or any method overridable (but only if Node is :unique ? clang warns even in shared_ptr case - false positive?)
    std.cout << static_pointer_cast<std.type_identity_t<Identifier>::element_type>(id_node).name  # this could also use 'asinstance' (dynamic_pointer_cast)
    args : [Node] = [id, id_node]
    args2 = [id, id_node] : Node   # ensure specifying type of list element instead of type of list works too
    static_cast<void>(args2)  # unused
    node = Node(id, args)
    std.cout << (node.args[0] == nullptr)
    std.cout << "\n" << node.repr()
    std.cout << node.args[0].repr()
)
    