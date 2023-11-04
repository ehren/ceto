# vim: syntax=python

include <map>
include <typeinfo>
include <numeric>
include <pybind11/pybind11.h>
include <pybind11/stl.h>

include(ast)
include(repr_visitors)
include(scope)


py: namespace = pybind11


def (class_name, node: Node.class:ptr:
    selph : py.object = py.cast(node)
    return std.string(py.str(selph.attr(c"__class__").attr(c"__name__")))
) : std.string

cpp'
PYBIND11_MODULE(_abstractsyntaxtree, m) {
'

# trick transpiler into local variable context
lambda(m : mut:auto:rref:
    pybind11.literals: using:namespace  # to bring in the `_a` literal

    # we don't want to define a virtual base class for Scope (defined in python). Nor do we want to expost py.class
#    node_scope_map : mut:static:std.map<Node:weak, py.object> = {}

    # Node:mut even though we're using Node aka Node:const (std::shared_ptr<const Node>) elsewhere - see https://github.com/pybind/pybind11/issues/131
    node : mut = py.class_<Node.class, Node:mut>(m, c"Node", py.dynamic_attr()).def_readwrite(
    c"func", &Node.func).def_readwrite(
    c"args", &Node.args).def_readwrite(
    c"declared_type", &Node.declared_type).def_readwrite(   #.def_property(
#    c"scope", lambda(s: const:py.object:ref:
#        thiz = s.cast<Node.class:ptr>()
#        strong = ceto.shared_from(thiz)
#        w : weak:Node = strong
#        node_scope_map[w]
#    ), lambda(s: const:py.object:ref, o:const:py.object:ref:
#        thiz = s.cast<Node.class:ptr>()
#        strong = ceto.shared_from(thiz)
#        w : weak:Node = strong
#        node_scope_map[w] = o
#        return
#        void()
#    )).def_readwrite(
    c"scope", &Node.scope).def_readwrite(
    c"source", &Node.source).def(
    c"__repr__", &Node.repr).def(
    c"ast_repr", lambda(n: Node.class:
        vis: mut = EvalableAstReprVisitor()
        n.accept(vis)
        vis.repr
    )).def_property_readonly(
    c"name", &Node.name).def_property(
    c"parent", &Node.parent, &Node.set_parent).def_readwrite(
    c"from_include", &Node.from_include)

    py.class_<UnOp.class, UnOp:mut>(m, c"UnOp", node).def(
        py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
        py.arg(c"op"), py.arg(c"args"), py.arg(c"source") = ("", 0)).def_readwrite(
        c"op", &UnOp.op)

    py.class_<LeftAssociativeUnOp.class, LeftAssociativeUnOp:mut>(m, c"LeftAssociativeUnOp", node).def(
        py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
        py.arg(c"op"), py.arg(c"args"), py.arg(c"source") = ("", 0)).def_readwrite(
        c"op", &LeftAssociativeUnOp.op)

    binop : mut = py.class_<BinOp.class, BinOp:mut>(m, c"BinOp", node)
    binop.def(py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
        py.arg(c"op"), py.arg(c"args"), py.arg(c"source") = ("", 0)).def_readwrite(
        c"op", &BinOp.op).def_property_readonly(
        c"lhs", &BinOp.lhs).def_property_readonly(
        c"rhs", &BinOp.rhs)

    typeop: mut = py.class_<TypeOp.class, TypeOp:mut>(m, c"TypeOp", binop)
    typeop.def(py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
               py.arg(c"op"), py.arg(c"args"), py.arg(c"source") = ("", 0))

    py.class_<SyntaxTypeOp.class, SyntaxTypeOp:mut>(m, c"SyntaxTypeOp", typeop).def(
        py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
        py.arg(c"op"), py.arg(c"args"), py.arg(c"source") = ("", 0)).def_readwrite(
        c"synthetic_lambda_return_lambda", &SyntaxTypeOp.synthetic_lambda_return_lambda)

    py.class_<AttributeAccess.class, AttributeAccess:mut>(m, c"AttributeAccess", binop).def(
        py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
        py.arg(c"op"), py.arg(c"args"), py.arg(c"source") = ("", 0))

    py.class_<ArrowOp.class, ArrowOp:mut>(m, c"ArrowOp", binop).def(
        py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
        py.arg(c"op"), py.arg(c"args"), py.arg(c"source") = ("", 0))

    py.class_<ScopeResolution.class, ScopeResolution:mut>(m, c"ScopeResolution", binop).def(
        py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
        py.arg(c"op"), py.arg(c"args"), py.arg(c"source") = ("", 0))

    assign:mut = py.class_<Assign.class, Assign:mut>(m, c"Assign", binop)
    assign.def(py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
    py.arg(c"op"), py.arg(c"args"), py.arg(c"source") = ("", 0))

    py.class_<NamedParameter.class, NamedParameter:mut>(m, c"NamedParameter", assign).def(
        py.init<const:string:ref, std.vector<Node>, std.tuple<string, int>>(),
        py.arg(c"op"), py.arg(c"args"), py.arg(c"source") = ("", 0))

    py.class_<Call.class, Call:mut>(m, c"Call", node).def(
        py.init<Node, std.vector<Node>, std.tuple<string, int>>(),
        py.arg(c"func"), py.arg(c"args"), py.arg(c"source") = ("", 0)).def_readwrite(
        c"is_one_liner_if", &Call.is_one_liner_if)

    py.class_<ArrayAccess.class, ArrayAccess:mut>(m, c"ArrayAccess", node).def(
        py.init<Node, std.vector<Node>, std.tuple<string, int>>(),
        py.arg(c"func"), py.arg(c"args"), py.arg(c"source") = ("", 0))

    py.class_<BracedCall.class, BracedCall:mut>(m, c"BracedCall", node).def(
        py.init<Node, std.vector<Node>, std.tuple<string, int>>(),
        py.arg(c"func"), py.arg(c"args"), py.arg(c"source") = ("", 0))

    py.class_<Template.class, Template:mut>(m, c"Template", node).def(
        py.init<Node, std.vector<Node>, std.tuple<string, int>>(),
        py.arg(c"func"), py.arg(c"args"), py.arg(c"source") = ("", 0))

    py.class_<Identifier.class, Identifier:mut>(m, c"Identifier", node).def(
        py.init<const:string:ref, std.tuple<string, int>>(),
        py.arg(c"name"), py.arg(c"source") = ("", 0))

    py.class_<StringLiteral.class, StringLiteral:mut>(m, c"StringLiteral", node).def(
        py.init<const:string:ref, Identifier, Identifier, std.tuple<string, int>>(),
        py.arg(c"str"), py.arg(c"prefix"), py.arg(c"suffix"), py.arg(c"source") = ("", 0)).def_readonly(
        c"str", &StringLiteral.str).def_readwrite(
        c"prefix", &StringLiteral.prefix).def_readwrite(
        c"suffix", &StringLiteral.suffix).def(
        c"escaped", &StringLiteral.escaped)

    py.class_<IntegerLiteral.class, IntegerLiteral:mut>(m, c"IntegerLiteral", node).def(
        py.init<const:string:ref, Identifier, std.tuple<string, int>>(),
        py.arg(c"integer_string"), py.arg(c"suffix"), py.arg(c"source") = ("", 0)).def_readonly(
        c"integer_string", &IntegerLiteral.integer_string).def_readonly(
        c"suffix", &IntegerLiteral.suffix)

    py.class_<FloatLiteral.class, FloatLiteral:mut>(m, c"FloatLiteral", node).def(
        py.init<const:string:ref, Identifier, std.tuple<string, int>>(),
        py.arg(c"float_string"), py.arg(c"suffix"), py.arg(c"source") = ("", 0)).def_readonly(
        c"float_string", &FloatLiteral.float_string).def_readonly(
        c"suffix", &FloatLiteral.suffix)

    list_like: mut = py.class_<ListLike_.class, ListLike_:mut>(m, c"ListLike_", node)

    py.class_<ListLiteral.class, ListLiteral:mut>(m, c"ListLiteral", list_like).def(
        py.init<std.vector<Node>, std.tuple<string, int>>(), py.arg(c"args"), py.arg(c"source") = ("", 0))

    py.class_<TupleLiteral.class, TupleLiteral:mut>(m, c"TupleLiteral", list_like).def(
        py.init<std.vector<Node>, std.tuple<string, int>>(), py.arg(c"args"), py.arg(c"source") = ("", 0))

    py.class_<BracedLiteral.class, BracedLiteral:mut>(m, c"BracedLiteral", list_like).def(
        py.init<std.vector<Node>, std.tuple<string, int>>(), py.arg(c"args"), py.arg(c"source") = ("", 0))

    block:mut = py.class_<Block.class, Block:mut>(m, c"Block", list_like)
    block.def(py.init<std.vector<Node>, std.tuple<string, int>>(), py.arg(c"args"), py.arg(c"source") = ("", 0))

    py.class_<Module.class, Module:mut>(m, c"Module", block).def(py.init<std.vector<Node>,
        std.tuple<string, int>>(), py.arg(c"args"), py.arg(c"source") = ("", 0)).def_readwrite(
        c"has_main_function", &Module.has_main_function)

    py.class_<RedundantParens.class, RedundantParens:mut>(m, c"RedundantParens", node).def(
        py.init<std.vector<Node>, std.tuple<string, int>>(), py.arg(c"args"), py.arg(c"source") = ("", 0))

    py.class_<InfixWrapper_.class, InfixWrapper_:mut>(m, c"InfixWrapper_", node).def(
        py.init<std.vector<Node>, std.tuple<string, int>>(), py.arg(c"args"), py.arg(c"source") = ("", 0))

    # Scope bindings:
    # These should probably go in a separate python module at some point (C++ namespace support would be more useful in general though)

    class_def: mut = py.class_<ClassDefinition.class, ClassDefinition:mut>(m, c"ClassDefinition").def(
        py.init<Identifier, Call, bool, bool, bool>(), py.arg(c"name_node"),
        py.arg(c"class_def_node"), py.arg(c"is_unique"), py.arg(c"is_struct"),
        py.arg(c"is_forward_declaration")).def_readwrite(
        c"name_node", &ClassDefinition.name_node).def_readwrite(
        c"class_def_node", &ClassDefinition.class_def_node).def_readwrite(
        c"is_unique", &ClassDefinition.is_unique).def_readwrite(
        c"is_struct", &ClassDefinition.is_struct).def_readwrite(
        c"is_forward_declaration", &ClassDefinition.is_forward_declaration).def_readwrite(
        c"is_concrete", &ClassDefinition.is_concrete).def_readwrite(
        c"is_pure_virtual", &ClassDefinition.is_pure_virtual).def(
        c"__repr__", &ClassDefinition.repr)

    py.class_<InterfaceDefinition.class, InterfaceDefinition:mut>(m, c"InterfaceDefinition", class_def).def(py.init<>())

    variable_def: mut = py.class_<VariableDefinition.class, VariableDefinition:mut>(m, c"VariableDefinition").def(
        py.init<Identifier, Node>(), py.arg(c"defined_node"), py.arg(c"defining_node")).def_readwrite(
        c"defined_node", &VariableDefinition.defined_node).def_readwrite(
        c"defining_node", &VariableDefinition.defining_node).def(
        c"__repr__", &VariableDefinition.repr)

    py.class_<LocalVariableDefinition.class, LocalVariableDefinition:mut>(m, c"LocalVariableDefinition", variable_def).def(
        py.init<Identifier, Node>(), py.arg(c"defined_node"), py.arg(c"defining_node"))

    py.class_<GlobalVariableDefinition.class, GlobalVariableDefinition:mut>(m, c"GlobalVariableDefinition", variable_def).def(
        py.init<Identifier, Node>(), py.arg(c"defined_node"), py.arg(c"defining_node"))

    py.class_<FieldDefinition.class, FieldDefinition:mut>(m, c"FieldDefinition", variable_def).def(
        py.init<Identifier, Node>(), py.arg(c"defined_node"), py.arg(c"defining_node"))

    py.class_<ParameterDefinition.class, ParameterDefinition:mut>(m, c"ParameterDefinition", variable_def).def(
        py.init<Identifier, Node>(), py.arg(c"defined_node"), py.arg(c"defining_node"))
#
    py.class_<Scope.class, Scope:mut>(m, c"Scope").def(
        py.init<>()).def_readwrite(
        c"indent", &Scope.indent).def_readwrite(
        c"in_function_body", &Scope.in_function_body).def_readwrite(
        c"in_function_param_list", &Scope.in_function_param_list).def_readwrite(
        c"in_class_body", &Scope.in_class_body).def_readwrite(
        c"in_decltype", &Scope.in_decltype).def(
        c"indent_str", &Scope.indent_str).def(
        c"add_variable_definition", &Scope.add_variable_definition, py.kw_only(), py.arg(c"defined_node"), py.arg(c"defining_node")).def(
        c"add_interface_method", &Scope.add_interface_method).def(
        c"add_class_definition", &Scope.add_class_definition).def(
        c"lookup_class", &Scope.lookup_class).def(
        c"find_defs", &Scope.find_defs, py.arg(c"var_node"), py.arg(c"find_all") = true).def(
        c"find_def", &Scope.find_def).def(
        c"enter_scope", &Scope.enter_scope).def_property_readonly(
        c"parent", &Scope.parent)

    m.def(c"creates_new_variable_scope", &creates_new_variable_scope)

    return
)(m)

cpp"}"  # end PYBIND11MODULE

