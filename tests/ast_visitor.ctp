# Test Output: BaseVisitor visiting Identifier
# Test Output: BaseVisitor visiting Node
# Test Output: BaseVisitor visiting ListLiteral
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

    def (visit: virtual:mut, node: Node:
        std.cout << "BaseVisitor visiting Node\n"
    )

    def (visit: virtual:mut, ident: Identifier:
        std.cout << "BaseVisitor visiting Identifier\n"
    )

    def (visit: virtual:mut, list_literal: ListLiteral:
        std.cout << "BaseVisitor visiting ListLiteral\n"
    )
)

class (Node:

    def (accept: virtual, visitor: BaseVisitor:mut:
        visitor.visit(self)
    )
)

class (Identifier(Node):
    _name : string

    def (init, name:
        self._name = name
    )

    def (accept: virtual, visitor: BaseVisitor:mut:
        visitor.visit(self)
    )
)

class (ListLiteral(Node):
    args : [Node]

    def (init, args:
        self.args = args
    )

    def (accept: virtual, visitor: BaseVisitor:mut:
        visitor.visit(self)
    )
)


class (RecordingVisitor(BaseVisitor):
    record = ""

    def (visit: virtual:mut, node: Node:
        self.record += "RecordingVisitor visiting Node\n"
    )

    def (visit: virtual:mut, ident: Identifier:
        self.record += "RecordingVisitor visiting Identifier\n"
    )

    def (visit: virtual:mut, list_literal: ListLiteral:
        self.record += "RecordingVisitor visiting ListLiteral\n"

        # in contrast to BaseVisitor, here we choose to traverse the children
        for (arg in list_literal.args:
            arg.accept(self)
        )
    )
)


def (main:
    node = Node()
    ident = Identifier("a")

    simple_visitor: mut = BaseVisitor()
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