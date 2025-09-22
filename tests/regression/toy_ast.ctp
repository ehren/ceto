# Test Output: aaa0
# Test Output: generic node with func identifier node with name: a
# Test Output: (2 args.)
# Test Output: arg: identifier node with name: a
# Test Output: arg: identifier node with name: a
# Test Output: identifier node with name: a


class (Node:
    func : Node
    args : [Node]
    
    # <strike>TODO</strike>no: "overridable" / "canoverride" / "yesoverride"? otherwise "final" by default
    # maybe TODO final by default
    def (repr: virtual:
        r : mut = s"generic node with func " + if (self.func: self.func.repr() else: s"none") + "(" + std.to_string(self.args.size()) + " args.)\n"
        for (a in self.args:
            r = r + "arg: " + a.repr()
        )
        return r
    ) : string
    
    # leaning towards no: "overridable" implies virtual destructor
    # debatable if we should make inheritance without a virtual destructor a transpiler level error (or at least a non-default)
    # clang warns if we omit this though the base has at least one virtual so dynamic_pointer_cast still works and we're always creating w/ make shared (in safe code) so no polymorphic deletion occurs
    def (destruct: virtual:
        pass
    )
    # one can always add virtual destructors to every class via the macro system (adding destructors if inherited from might be possible but defmacros that intentionally require multiple passes will be ugly at least right now)
)

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
    unsafe.extern(static_pointer_cast, ceto.get_underlying)
    # perhaps somewat dubious that we allow std.type_identity_t given it allows wacky code (digging into the smart pointer implememntation even if statically like below).

    id = Identifier("a")
    std.cout << id.name
    id_node : Node = Identifier("a")  # TODO virtual destructor in Node if overridable or any method overridable (but only if Node is :unique ? clang warns even in shared_ptr case - false positive?)
    std.cout << static_pointer_cast<std.type_identity_t<Identifier>::element_type>(ceto.get_underlying(id_node)).name  # this could/should use 'asinstance' (dynamic_pointer_cast). good testcase though (will break if e.g. non_null by default added)
    std.cout << asinstance(id_node, Identifier).name
    args : [Node] = [id, id_node]
    args2 = [id, id_node] : Node   # ensure specifying type of list element instead of type of list works too
    static_cast<void>(args2)  # unused
    node = Node(id, args)
    std.cout << (node.args[0] == nullptr)
    std.cout << "\n" << node.repr()
    std.cout << node.args[0].repr()
)
    
