# vim: syntax=python

include <map>
include <typeinfo>
include <numeric>
include <pybind11/pybind11.h>
include <pybind11/stl.h>
include <pybind11/stl_bind.h>

include(ast)

#PYBIND11_MAKE_OPAQUE(std.map<std.string, Node>)

include(repr_visitors)
include(scope)
include(parser)
include(macro_matcher)


py: namespace = pybind11


def (class_name, node: Node.class:ptr:
    selph : py.object = py.cast(node)
    return std.string(py.str(selph.attr("__class__").attr("__name__")))
) : std.string

def (module_path:
    acquire = py.gil_scoped_acquire()
    module: py.object = py.module.import("ceto");
    os: py.object = py.module.import("os");
    exeloc = module.attr("__file__")
    dir = os.attr("path").attr(exeloc)
    return dir.cast<std.string>();
)

cpp'
PYBIND11_MODULE(_abstractsyntaxtree, m) {
'

# trick transpiler into local variable context
lambda(m : mut:auto:rref:

    pybind11.literals: using:namespace  # to bring in the `_a` literal

    # Node:mut even though we're using Node aka Node:const (std::shared_ptr<const Node>) elsewhere - see https://github.com/pybind/pybind11/issues/131
    node : mut = py.class_<Node.class, Node:mut>(m, "Node").def_readwrite(
    "func", &Node.func).def_readwrite(
    "args", &Node.args).def_readwrite(
    "declared_type", &Node.declared_type).def_readwrite(   #.def_property(
    "scope", &Node.scope).def_readwrite(
    "source", &Node.source).def(
    "__repr__", &Node.repr).def(
    "ast_repr", lambda(n: Node.class:
        vis: mut = EvalableAstReprVisitor()
        n.accept(vis)
        vis.repr
    )).def_property_readonly(
    "name", &Node.name).def_property(
    "parent", &Node.parent, &Node.set_parent).def_readwrite(
    "file_path", &Node.file_path)

    py.class_<UnOp.class, UnOp:mut>(m, "UnOp", node).def(
        py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
        py.arg("op"), py.arg("args"), py.arg("source") = ("", 0)).def_readwrite(
        "op", &UnOp.op)

    py.class_<LeftAssociativeUnOp.class, LeftAssociativeUnOp:mut>(m, "LeftAssociativeUnOp", node).def(
        py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
        py.arg("op"), py.arg("args"), py.arg("source") = ("", 0)).def_readwrite(
        "op", &LeftAssociativeUnOp.op)

    binop : mut = py.class_<BinOp.class, BinOp:mut>(m, "BinOp", node)
    binop.def(py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
        py.arg("op"), py.arg("args"), py.arg("source") = ("", 0)).def_readwrite(
        "op", &BinOp.op).def_property_readonly(
        "lhs", &BinOp.lhs).def_property_readonly(
        "rhs", &BinOp.rhs)

    typeop: mut = py.class_<TypeOp.class, TypeOp:mut>(m, "TypeOp", binop)
    typeop.def(py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
               py.arg("op"), py.arg("args"), py.arg("source") = ("", 0))

    py.class_<SyntaxTypeOp.class, SyntaxTypeOp:mut>(m, "SyntaxTypeOp", typeop).def(
        py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
        py.arg("op"), py.arg("args"), py.arg("source") = ("", 0)).def_readwrite(
        "synthetic_lambda_return_lambda", &SyntaxTypeOp.synthetic_lambda_return_lambda)

    py.class_<AttributeAccess.class, AttributeAccess:mut>(m, "AttributeAccess", binop).def(
        py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
        py.arg("op"), py.arg("args"), py.arg("source") = ("", 0))

    py.class_<ArrowOp.class, ArrowOp:mut>(m, "ArrowOp", binop).def(
        py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
        py.arg("op"), py.arg("args"), py.arg("source") = ("", 0))

    py.class_<ScopeResolution.class, ScopeResolution:mut>(m, "ScopeResolution", binop).def(
        py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
        py.arg("op"), py.arg("args"), py.arg("source") = ("", 0))

    assign:mut = py.class_<Assign.class, Assign:mut>(m, "Assign", binop)
    assign.def(py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
    py.arg("op"), py.arg("args"), py.arg("source") = ("", 0))

    py.class_<NamedParameter.class, NamedParameter:mut>(m, "NamedParameter", assign).def(
        py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
        py.arg("op"), py.arg("args"), py.arg("source") = ("", 0))

    py.class_<Call.class, Call:mut>(m, "Call", node).def(
        py.init<Node, std.vector<Node>, std.tuple<string, int>>(),
        py.arg("func"), py.arg("args"), py.arg("source") = ("", 0)).def_readwrite(
        "is_one_liner_if", &Call.is_one_liner_if)

    py.class_<ArrayAccess.class, ArrayAccess:mut>(m, "ArrayAccess", node).def(
        py.init<Node, std.vector<Node>, std.tuple<string, int>>(),
        py.arg("func"), py.arg("args"), py.arg("source") = ("", 0))

    py.class_<BracedCall.class, BracedCall:mut>(m, "BracedCall", node).def(
        py.init<Node, std.vector<Node>, std.tuple<string, int>>(),
        py.arg("func"), py.arg("args"), py.arg("source") = ("", 0))

    py.class_<Template.class, Template:mut>(m, "Template", node).def(
        py.init<Node, std.vector<Node>, std.tuple<string, int>>(),
        py.arg("func"), py.arg("args"), py.arg("source") = ("", 0))

    py.class_<Identifier.class, Identifier:mut>(m, "Identifier", node).def(
        py.init<const:string:ref, std.tuple<string, int>>(),
        py.arg("name"), py.arg("source") = ("", 0))

    py.class_<StringLiteral.class, StringLiteral:mut>(m, "StringLiteral", node).def(
        py.init<const:string:ref, Identifier, Identifier, std.tuple<string, int>>(),
        py.arg("str"), py.arg("prefix"), py.arg("suffix"), py.arg("source") = ("", 0)).def_readonly(
        "str", &StringLiteral.str).def_readwrite(
        "prefix", &StringLiteral.prefix).def_readwrite(
        "suffix", &StringLiteral.suffix).def(
        "escaped", &StringLiteral.escaped)

    py.class_<IntegerLiteral.class, IntegerLiteral:mut>(m, "IntegerLiteral", node).def(
        py.init<const:string:ref, Identifier, std.tuple<string, int>>(),
        py.arg("integer_string"), py.arg("suffix"), py.arg("source") = ("", 0)).def_readonly(
        "integer_string", &IntegerLiteral.integer_string).def_readonly(
        "suffix", &IntegerLiteral.suffix)

    py.class_<FloatLiteral.class, FloatLiteral:mut>(m, "FloatLiteral", node).def(
        py.init<const:string:ref, Identifier, std.tuple<string, int>>(),
        py.arg("float_string"), py.arg("suffix"), py.arg("source") = ("", 0)).def_readonly(
        "float_string", &FloatLiteral.float_string).def_readonly(
        "suffix", &FloatLiteral.suffix)

    list_like: mut = py.class_<ListLike_.class, ListLike_:mut>(m, "ListLike_", node)

    py.class_<ListLiteral.class, ListLiteral:mut>(m, "ListLiteral", list_like).def(
        py.init<std.vector<Node>, std.tuple<string, int>>(), py.arg("args"), py.arg("source") = ("", 0))

    py.class_<TupleLiteral.class, TupleLiteral:mut>(m, "TupleLiteral", list_like).def(
        py.init<std.vector<Node>, std.tuple<string, int>>(), py.arg("args"), py.arg("source") = ("", 0))

    py.class_<BracedLiteral.class, BracedLiteral:mut>(m, "BracedLiteral", list_like).def(
        py.init<std.vector<Node>, std.tuple<string, int>>(), py.arg("args"), py.arg("source") = ("", 0))

    block:mut = py.class_<Block.class, Block:mut>(m, "Block", list_like)
    block.def(py.init<std.vector<Node>, std.tuple<string, int>>(), py.arg("args"), py.arg("source") = ("", 0))

    py.class_<Module.class, Module:mut>(m, "Module", block).def(py.init<std.vector<Node>,
        std.tuple<string, int>>(), py.arg("args"), py.arg("source") = ("", 0)).def_readwrite(
        "has_main_function", &Module.has_main_function)

    py.class_<RedundantParens.class, RedundantParens:mut>(m, "RedundantParens", node).def(
        py.init<std.vector<Node>, std.tuple<string, int>>(), py.arg("args"), py.arg("source") = ("", 0))

    py.class_<InfixWrapper_.class, InfixWrapper_:mut>(m, "InfixWrapper_", node).def(
        py.init<std.vector<Node>, std.tuple<string, int>>(), py.arg("args"), py.arg("source") = ("", 0))

    # Scope bindings:
    # These should probably go in a separate python module at some point (C++ namespace support would be more useful in general though)

    class_def: mut = py.class_<ClassDefinition.class, ClassDefinition:mut>(m, "ClassDefinition").def(
        py.init<Identifier, Call, bool, bool, bool>(), py.arg("name_node"),
        py.arg("class_def_node"), py.arg("is_unique"), py.arg("is_struct"),
        py.arg("is_forward_declaration")).def_readwrite(
        "name_node", &ClassDefinition.name_node).def_readwrite(
        "class_def_node", &ClassDefinition.class_def_node).def_readwrite(
        "is_unique", &ClassDefinition.is_unique).def_readwrite(
        "is_struct", &ClassDefinition.is_struct).def_readwrite(
        "is_forward_declaration", &ClassDefinition.is_forward_declaration).def_readwrite(
        "is_concrete", &ClassDefinition.is_concrete).def_readwrite(
        "is_pure_virtual", &ClassDefinition.is_pure_virtual).def(
        "__repr__", &ClassDefinition.repr)

    py.class_<InterfaceDefinition.class, InterfaceDefinition:mut>(m, "InterfaceDefinition", class_def).def(py.init<>())

    variable_def: mut = py.class_<VariableDefinition.class, VariableDefinition:mut>(m, "VariableDefinition").def(
        py.init<Identifier, Node>(), py.arg("defined_node"), py.arg("defining_node")).def_readwrite(
        "defined_node", &VariableDefinition.defined_node).def_readwrite(
        "defining_node", &VariableDefinition.defining_node).def(
        "__repr__", &VariableDefinition.repr)

    py.class_<LocalVariableDefinition.class, LocalVariableDefinition:mut>(m, "LocalVariableDefinition", variable_def).def(
        py.init<Identifier, Node>(), py.arg("defined_node"), py.arg("defining_node"))

    py.class_<GlobalVariableDefinition.class, GlobalVariableDefinition:mut>(m, "GlobalVariableDefinition", variable_def).def(
        py.init<Identifier, Node>(), py.arg("defined_node"), py.arg("defining_node"))

    py.class_<FieldDefinition.class, FieldDefinition:mut>(m, "FieldDefinition", variable_def).def(
        py.init<Identifier, Node>(), py.arg("defined_node"), py.arg("defining_node"))

    py.class_<ParameterDefinition.class, ParameterDefinition:mut>(m, "ParameterDefinition", variable_def).def(
        py.init<Identifier, Node>(), py.arg("defined_node"), py.arg("defining_node"))
#
    py.class_<Scope.class, Scope:mut>(m, "Scope").def(
        py.init<>()).def_readwrite(
        "indent", &Scope.indent).def_readwrite(
        "in_function_body", &Scope.in_function_body).def_readwrite(
        "in_function_param_list", &Scope.in_function_param_list).def_readwrite(
        "in_class_body", &Scope.in_class_body).def_readwrite(
        "in_decltype", &Scope.in_decltype).def(
        "indent_str", &Scope.indent_str).def(
        "add_variable_definition", &Scope.add_variable_definition, "defined_node"_a, "defining_node"_a).def(
        "add_interface_method", &Scope.add_interface_method).def(
        "add_class_definition", &Scope.add_class_definition).def(
        "lookup_class", &Scope.lookup_class).def(
        "find_defs", &Scope.find_defs, py.arg("var_node"), py.arg("find_all") = true).def(
        "find_def", &Scope.find_def).def(
        "enter_scope", &Scope.enter_scope).def_property_readonly(
        "parent", &Scope.parent)

    m.def("creates_new_variable_scope", &creates_new_variable_scope)

    # this will need its own module - just for testing for now
    m.def("parse_test", &parse_test)

    py.bind_map<std.map<std.string, Node>>(m, "StringNodeMap");

    m.def("macro_matches", &macro_matches)

    return
)(m)

cpp"}"  # end PYBIND11MODULE

