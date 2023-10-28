# Test Output: visiting Identifier
# Test Output: visiting Node
# Test Output: recording Ident visit
# Test Output: recording Node visit
# Test Output: recording Ident visit
# Test Output: recording Ident visit
# Test Output: recording Ident visit


class (Node)
class (Identifier)
class (ListLiteral)


class (BaseVisitor:
    def (visit: virtual:mut, node: Node:
        std.cout << "visiting Node\n"
    )

    def (visit: virtual:mut, ident: Identifier:
        std.cout << "visiting Identifier\n"
    )

    def (visit: virtual:mut, list_literal: ListLiteral:
        std.cout << "visiting ListLiteral\n"
        # here we're choosing not to visit the children of list_literal to
        # contrast with the behavior of RecordingVisitor
        # (and to avoid needing to define currently unsupported out of line methods...)
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
        self.record += "recording Node visit\n"
    )

    def (visit: virtual:mut, ident: Identifier:
        self.record += "recording Ident visit\n"
    )

    def (visit: virtual:mut, list_literal: ListLiteral:
        std.cout << "visiting ListLiteral\n"

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