import pdb
import typing
from collections import defaultdict
from .abstractsyntaxtree import Identifier, Call, Node, Assign, Block, Module, ArrayAccess

try:
    from ._abstractsyntaxtree import ClassDefinition, InterfaceDefinition, VariableDefinition, LocalVariableDefinition, GlobalVariableDefinition, ParameterDefinition, FieldDefinition, FunctionDefinition, NamespaceDefinition, creates_new_variable_scope, Scope, comes_before
except ImportError:
    raise

    class ClassDefinition:

        def __init__(self, name_node : Identifier, class_def_node: Call, is_unique, is_struct, is_forward_declaration):
            self.name_node = name_node
            self.class_def_node = class_def_node
            self.is_unique = is_unique
            self.is_struct = is_struct
            self.is_forward_declaration = is_forward_declaration
            self.is_concrete = False
            self.is_pure_virtual = False
            # if self.is_unique and self.is_struct:
            #     raise SemanticAnalysisError("structs may not be marked unique", class_def_node)

        # def has_generic_params(self):
        #     return True in self.is_generic_param_index.values()

        def __repr__(self):
            return f"{self.__class__.__name__}({self.name_node}, {self.class_def_node}, {self.is_unique}, {self.is_struct}, {self.is_forward_declaration})"


    class InterfaceDefinition(ClassDefinition):
        def __init__(self):
            super().__init__(None, None, False, False, False)


    class VariableDefinition:

        def __init__(self, defined_node: Identifier, defining_node: Node):
            self.defined_node = defined_node
            self.defining_node = defining_node

        def __repr__(self):
            return f"{self.__class__.__name__}({self.defined_node}, {self.defining_node})"


    class LocalVariableDefinition(VariableDefinition):
        pass


    class GlobalVariableDefinition(VariableDefinition):
        pass


    class FieldDefinition(VariableDefinition):
        pass


    class ParameterDefinition(VariableDefinition):
        pass


    def creates_new_variable_scope(e: Node) -> bool:
        if isinstance(e, Call):
            if e.func.name in ["def", "lambda", "class", "struct"]:
                return True
            elif isinstance(e.func, ArrayAccess) and e.func.func.name == "lambda":
                return True
        return False


    def _node_depth(node):
        if node.parent:
            # if node in node.parent.args and isinstance(node.parent, Block):
            #if isinstance(node.parent, (Block, Call)) and node in node.parent.args:
            if node in node.parent.args:
                return node.parent.args.index(node) + 1+ _node_depth(node.parent)
            # elif isinstance(node, Block) and isinstance(node.parent, Call) and node in node.parent.args:
            #     return node.parent.args.index(node) + _node_depth(node.parent)
            else:
                return _node_depth(node.parent)
        else:
            return 0


    def comes_before(root, before, after):
        if root is before:
            return True
        elif root is after:
            return False
        for arg in root.args:
            cb = comes_before(arg, before, after)
            if cb is not None:
                return cb
        if root.func:
            cb = comes_before(root.func, before, after)
            if cb is not None:
                return cb
        return None


    class Scope:

        def __init__(self):
            super().__init__()
            self.interfaces = defaultdict(list)
            self.class_definitions = []
            self.variable_definitions = []
            self.indent = 0
            self.parent : Scope = None
            self.in_function_body = False
            self.in_function_param_list = False  # TODO unused remove
            self.in_class_body = False
            self.in_decltype = False

        def indent_str(self):
            return "    " * self.indent

        def add_variable_definition(self, defined_node: Identifier, defining_node: Node):
            assert isinstance(defined_node, Identifier)
            assert isinstance(defining_node, Node)

            var_class = GlobalVariableDefinition
            parent = defined_node#.parent
            while parent:
                # if isinstance(parent, Block):
                #     var_class = LocalVariableDefinition
                #     break
                if creates_new_variable_scope(parent):
                    if parent.func.name in ["class", "struct"]:
                        var_class = FieldDefinition
                    elif parent.func.name in ["def", "lambda"]:
                        var_class = ParameterDefinition
                    else:
                        var_class = LocalVariableDefinition
                    break

                parent = parent.parent

            self.variable_definitions.append(var_class(defined_node, defining_node))

        def add_interface_method(self, interface_name: str, interface_method_def_node: Node):
            self.interfaces[interface_name].append(interface_method_def_node)

        def add_class_definition(self, class_definition: ClassDefinition):
            self.class_definitions.append(class_definition)

        def lookup_class(self, class_node) -> typing.Optional[ClassDefinition]:
            if not isinstance(class_node, Identifier):
                return None
            for c in self.class_definitions:
                if isinstance(c.name_node, Identifier) and c.name_node.name == class_node.name:
                    return c
            if class_node.name in self.interfaces:
                return InterfaceDefinition()
            if self.parent:
                return self.parent.lookup_class(class_node)
            return None

        def find_defs(self, var_node):
            if not isinstance(var_node, Identifier):
                return

            for d in self.variable_definitions:
                if d.defined_node.name == var_node.name and d.defined_node is not var_node:
                    _ , defined_loc = d.defined_node.source
                    _ , var_loc = var_node.source

                    parent_block = d.defined_node.parent
                    while True:
                        if isinstance(parent_block, Module):
                            break
                        parent_block = parent_block.parent

                    defined_before = comes_before(parent_block, d.defined_node, var_node)

                    # this fires on invalid code 'test_requires_bad'
                    if (defined_loc < var_loc) != defined_before:
                        # from .semanticanalysis import SemanticAnalysisError
                        # raise SemanticAnalysisError(f"broken defs / scoping. You likely have broken code somewhere involving the variable {var_node.name}.", var_node)
                        pass
                    if defined_before:
                        yield d
                        if isinstance(d.defining_node, Assign) and isinstance(d.defining_node.rhs, Identifier):
                            yield from self.find_defs(d.defining_node.rhs)

            if self.parent is not None:
                yield from self.parent.find_defs(var_node)

        def find_def(self, var_node):
            for d in self.find_defs(var_node):
                return d

        def enter_scope(self):
            s = Scope()
            s.parent = self
            s.in_function_body = self.in_function_body
            s.in_decltype = self.in_decltype
            s.indent = self.indent + 1
            return s


