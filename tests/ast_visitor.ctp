# Test Output: visiting Identifier
# Test Output: visiting Node
# Test Output: recording Ident visit
# Test Output: recording Node visit


class (Node)
class (Identifier)


class (BaseVisitor:
    def (visit: virtual:mut, node: Node:
        std.cout << "visiting Node\n"
    )

    def (visit: virtual:mut, ident: Identifier:
        std.cout << "visiting Identifier\n"
    )
)

class (RecordingVisitor(BaseVisitor):
    record = ""

    def (visit: virtual:mut, node: Node:
        self.record += "recording Node visit\n"
    )

    def (visit: virtual:mut, ident: Identifier:
        self.record += "recording Ident visit\n"
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


def (main:
    node = Node()
    ident = Identifier("a")

    visitor: mut = BaseVisitor()
    ident.accept(visitor)
    node.accept(visitor)

    recording_visitor: mut = RecordingVisitor()
    ident.accept(recording_visitor)
    node.accept(recording_visitor)
    std.cout << recording_visitor.record
)