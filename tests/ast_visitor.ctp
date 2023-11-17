# Test Output: SimpleVisitor visiting Identifier
# Test Output: SimpleVisitor visiting Node
# Test Output: SimpleVisitor visiting ListLiteral
# Test Output: RecordingVisitor visiting Identifier
# Test Output: RecordingVisitor visiting Node
# Test Output: RecordingVisitor visiting ListLiteral
# Test Output: RecordingVisitor visiting Identifier
# Test Output: RecordingVisitor visiting Identifier
# Test Output: RecordingVisitor visiting Identifier

class (Node)
class (Identifier)
class (ListLiteral)

class (BaseVisitor:

    def (visit: virtual:mut, node: Node): void = 0

    def (visit: virtual:mut, ident: Identifier): void = 0

    def (visit: virtual:mut, list_literal: ListLiteral): void = 0
)

class (Node:

    def (accept: virtual, visitor: BaseVisitor:mut:
        visitor.visit(self)
    )
)

class (Identifier(Node):
    name : string

    def (accept: virtual, visitor: BaseVisitor:mut:
        visitor.visit(self)
    )
)

class (ListLiteral(Node):
    args : [Node]

    def (accept: virtual, visitor: BaseVisitor:mut:
        visitor.visit(self)
    )
)

class (SimpleVisitor(BaseVisitor):
    def (visit: virtual:mut, node: Node:
        std.cout << "SimpleVisitor visiting Node\n"
    )

    def (visit: virtual:mut, ident: Identifier:
        std.cout << "SimpleVisitor visiting Identifier\n"
    )

    def (visit: virtual:mut, list_literal: ListLiteral:
        std.cout << "SimpleVisitor visiting ListLiteral\n"
        # here we're choosing not to traverse the children (in contrast to RecordingVisitor)
    )
)

class (RecordingVisitor(BaseVisitor):
    record = s""

    def (visit: virtual:mut, node: Node:
        self.record += "RecordingVisitor visiting Node\n"
    )

    def (visit: virtual:mut, ident: Identifier:
        self.record += "RecordingVisitor visiting Identifier\n"
    )

    def (visit: virtual:mut, list_literal: ListLiteral:
        self.record += "RecordingVisitor visiting ListLiteral\n"

        for (arg in list_literal.args:
            arg.accept(self)
        )
    )
)

def (main:
    node = Node()
    ident = Identifier("a")

    simple_visitor: mut = SimpleVisitor()
    ident.accept(simple_visitor)
    node.accept(simple_visitor)

    recording_visitor: mut = RecordingVisitor()
    ident.accept(recording_visitor)
    node.accept(recording_visitor)

    list_args : [Node] = [ident, ident, ident]
    list_literal = ListLiteral(list_args)
    list_literal.accept(simple_visitor)
    list_literal.accept(recording_visitor)

    std.cout << recording_visitor.record
)
