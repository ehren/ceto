# Test Output: a

cpp'
#include <map>
'

    
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

def (macro_trampoline, fptr : uintptr_t, matches: std.map<string, Node:mut>:
    # test case from selfhost (complicated scope and TypeOp vs .declared type lambda capture bug)
    # f2 = reinterpret_cast<decltype(+(lambda(matches:std.map<string, Node:mut>, None): Node:mut))>(fptr)  # extra parenthese due to + : precedence (this should work)
    # return (*f2)(matches)
    pass
)

def (main:
    id = Identifier("a")
    std.cout << id.name().value()
    
    f2 = reinterpret_cast<decltype(+(lambda(matches:std.map<string, Node:mut>, None): Node:mut))>(0)  
)
    
    