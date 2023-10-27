# Test Output: a

include <map>

class (Node:
    func : Node
    args : [Node]

    # def (repr: virtual) = 0  # error declarations must specify a return type
    def (repr: virtual) : string = 0
    
    def (name: virtual:
        return None
    ) : std.optional<string>
)

class (Identifier(Node):
    _name : string

    def (init, name:
        self._name = name
        super.init(None, [] : Node)
    )

    def (repr:
        return self._name
    ) : decltype(static_cast<Node>(None).repr())  # TODO this should be automatic if repr has 'override' specifier and no return type (though static_cast instead of static_pointer_cast is pretty sketchy)

    def (name: virtual:
        return self._name
    ) : decltype(std.declval<Node>().name())  # this is surely better (note that Node printed as shared_ptr<const(?) Node> here)
)

def (example_macro_body_workaround_no_fptr_syntax_yet, matches: std.map<string, Node>:
    return None
) : Node

glob = 0

def (macro_trampoline, fptr : uintptr_t, matches: std.map<string, Node>:
    # test case from selfhost (complicated scope and TypeOp vs .declared type lambda capture bug)

    #f = reinterpret_cast<decltype(+lambda(matches:std.map<string, Node>, None): Node)>(fptr)   # NOTE post-parse hacks for typed lambda only work for immediately invoked lambda aka Call node (not needed for assign case due to lower precedence =). : codegen.CodeGenError: ('unexpected typed construct', UnOp(+)([lambda(matches,Block((return : None)))]))
    # ^ debatable if needs fix for this case (all current post-parse lambda precedence hacks are dubious and at the least TODO should be moved out of codegen to prevent future breakage)

    # use extra parenthesese for correct precedence (because a return type is specified)
    f = reinterpret_cast<decltype(+(lambda(matches:std.map<string, Node>, None): Node))>(fptr)  # that fptr had a previous def unsurfaced a seemingly now fixed lambda capture bug.
    f2 = reinterpret_cast<decltype(+(lambda(matches:std.map<string, Node>, None): Node))>(0)
    f3 = reinterpret_cast<decltype(+(lambda(matches:std.map<string, Node>, None): Node))>(glob)
    f4 = &example_macro_body_workaround_no_fptr_syntax_yet
    static_assert(std.is_same_v<decltype(f), decltype(f2)>)
    static_assert(std.is_same_v<decltype(f), decltype(f3)>)
    static_assert(std.is_same_v<decltype(f), decltype(f4)>)
    return (*f)(matches)
)

def (main:
    id = Identifier("a")
    std.cout << id.name().value()
)
    
    