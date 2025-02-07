# visiting Identifier a
# visiting Add
# visiting Identifier a
# visiting Node
# visiting Identifier a

class (Node)
class (Identifier)
class (BinOp)
class (Add)

class (Visitor:

    def (visit: virtual:mut, node: Node): void = 0

    def (visit: virtual:mut, node: Identifier): void = 0

    def (visit: virtual:mut, node: BinOp): void = 0

    def (visit: virtual:mut, node: Add): void = 0
)

class (Node:
    loc : int

    def (accept: virtual, visitor: Visitor:mut:
        visitor.visit(self)
    )
)

class (Identifier(Node):
    name : std.string

    def (init, name, loc=0:
        # a user defined constructor is present - 1-arg constructor of Node is not inherited
        self.name = name  # implicitly occurs in initializer list
        super.init(loc)   # same
    )

    def (accept: virtual, visitor: Visitor:mut:
        visitor.visit(self)
    )
)

class (BinOp(Node):
    args : [Node]

    def (init, args, loc=0:
        self.args = args
        super.init(loc)
    )

    def (accept: virtual, visitor: Visitor:mut:
        visitor.visit(self)
    )
)

class (Add(BinOp):
    # inherits 2-arg constructor from BinOp (because no user defined init is present)

    def (accept: virtual, visitor: Visitor:mut:
        visitor.visit(self)
    )
)

class (SimpleVisitor(Visitor):
    record = s""

    def (visit: virtual:mut, node: Node:
        self.record += "visiting Node\n"
    )

    def (visit: virtual:mut, ident: Identifier:
        self.record += "visiting Identifier " + ident.name + "\n"
    )

    def (visit: virtual:mut, node: BinOp:
        self.record += "visiting BinOp\n"

        args: mut:auto:ref:ref = node.args
        for (arg in args:
            arg.accept(self)
        )
    )

    def (visit: virtual:mut, node: Add:
        self.record += "visiting Add\n"

        args: mut:auto:ref:ref = node.args
        for (arg in args:
            arg.accept(self)
        )
    )
)

def (main:
    node = Node(0)
    ident = Identifier("a", 5)
    args: [Node] = [ident, node, ident]
    add: Add = Add(args)

    simple_visitor: mut = SimpleVisitor()
    ident.accept(simple_visitor)
    add.accept(simple_visitor)

    std.cout << simple_visitor.record
)
