# vim: syntax=python

include <map>
include <typeinfo>
include <numeric>
include <pybind11/pybind11.h>
include <pybind11/stl.h>
include <pybind11/stl_bind.h>
include <pybind11/functional.h>

include(ast)
include(scope)
include(evalable_repr)
include(parser)
include(macro_expansion)

unsafe()

py: namespace = pybind11


def (module_path:
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

    py.class_<Source.class, Source:mut>(m, "Source").def(
        py.init<>()).def_readwrite(
        "source", &Source.source)

    py.class_<SourceLoc>(m, "SourceLoc").def(
        py.init<Source, int>(), py.arg("source") = None, py.arg("loc") = 0).def_readwrite(
        "source", &SourceLoc.source).def_readwrite(
        "loc", &SourceLoc.loc).def_readwrite(
        "header_file_cth", &SourceLoc.header_file_cth).def_readwrite(
        "header_file_h", &SourceLoc.header_file_h)

    # Node:mut even though we're using Node aka Node:const (std::shared_ptr<const Node>) elsewhere - see https://github.com/pybind/pybind11/issues/131
    node : mut = py.class_<Node.class, Node:mut>(m, "Node").def_readwrite(
    "func", &Node.func).def_readwrite(
    "args", &Node.args).def_readwrite(
    "declared_type", &Node.declared_type).def_readwrite(
    "scope", &Node.scope).def_readwrite(
    "source", &Node.source).def(
    "clone", &Node.clone).def(
    "__repr__", &Node.repr).def(
    "ast_repr", lambda(n: Node.class, preserve_source_loc: bool, ceto_evalable: bool:
        vis: mut = EvalableAstReprVisitor(preserve_source_loc, ceto_evalable)
        n.accept(vis)
        vis.repr
    ), py.arg("preserve_source_loc") = true, py.arg("ceto_evalable") = false).def_property_readonly(
    "name", &Node.name).def_property(
    "parent", &Node.parent, &Node.set_parent)

    py.class_<UnOp.class, UnOp:mut>(m, "UnOp", node).def(
        py.init<const:string:ref, const:std.vector<Node>:ref, const:SourceLoc:ref>(),
        py.arg("op"), py.arg("args"), py.arg("source") = SourceLoc()).def_readwrite(
        "op", &UnOp.op)

    py.class_<LeftAssociativeUnOp.class, LeftAssociativeUnOp:mut>(m, "LeftAssociativeUnOp", node).def(
        py.init<const:string:ref, const:std.vector<Node>:ref, const:SourceLoc:ref>(),
        py.arg("op"), py.arg("args"), py.arg("source") = SourceLoc()).def_readwrite(
        "op", &LeftAssociativeUnOp.op)

    binop : mut = py.class_<BinOp.class, BinOp:mut>(m, "BinOp", node)
    binop.def(py.init<const:string:ref, const:std.vector<Node>:ref, const:SourceLoc:ref>(),
        py.arg("op"), py.arg("args"), py.arg("source") = SourceLoc()).def_readwrite(
        "op", &BinOp.op).def_property_readonly(
        "lhs", &BinOp.lhs).def_property_readonly(
        "rhs", &BinOp.rhs)

    typeop: mut = py.class_<TypeOp.class, TypeOp:mut>(m, "TypeOp", binop)
    typeop.def(py.init<const:string:ref, const:std.vector<Node>:ref, const:SourceLoc:ref>(),
               py.arg("op"), py.arg("args"), py.arg("source") = SourceLoc())

    py.class_<SyntaxTypeOp.class, SyntaxTypeOp:mut>(m, "SyntaxTypeOp", typeop).def(
        py.init<const:string:ref, const:std.vector<Node>:ref, const:SourceLoc:ref>(),
        py.arg("op"), py.arg("args"), py.arg("source") = SourceLoc()).def_readwrite(
        "synthetic_lambda_return_lambda", &SyntaxTypeOp.synthetic_lambda_return_lambda)

    py.class_<AttributeAccess.class, AttributeAccess:mut>(m, "AttributeAccess", binop).def(
        py.init<const:string:ref, const:std.vector<Node>:ref, const:SourceLoc:ref>(),
        py.arg("op"), py.arg("args"), py.arg("source") = SourceLoc())

    py.class_<ArrowOp.class, ArrowOp:mut>(m, "ArrowOp", binop).def(
        py.init<const:string:ref, const:std.vector<Node>:ref, const:SourceLoc:ref>(),
        py.arg("op"), py.arg("args"), py.arg("source") = SourceLoc())

    py.class_<ScopeResolution.class, ScopeResolution:mut>(m, "ScopeResolution", binop).def(
        py.init<const:string:ref, const:std.vector<Node>:ref, const:SourceLoc:ref>(),
        py.arg("op"), py.arg("args"), py.arg("source") = SourceLoc())

    py.class_<BitwiseOrOp.class, BitwiseOrOp:mut>(m, "BitwiseOrOp", binop).def(
        py.init<const:string:ref, const:std.vector<Node>:ref, const:SourceLoc:ref>(),
        py.arg("op"), py.arg("args"), py.arg("source") = SourceLoc())

    py.class_<EqualsCompareOp.class, EqualsCompareOp:mut>(m, "EqualsCompareOp", binop).def(
        py.init<const:string:ref, const:std.vector<Node>:ref, const:SourceLoc:ref>(),
        py.arg("op"), py.arg("args"), py.arg("source") = SourceLoc())

    assign:mut = py.class_<Assign.class, Assign:mut>(m, "Assign", binop)
    assign.def(py.init<const:string:ref, const:std.vector<Node>:ref, const:SourceLoc:ref>(),
    py.arg("op"), py.arg("args"), py.arg("source") = SourceLoc())

    py.class_<NamedParameter.class, NamedParameter:mut>(m, "NamedParameter", assign).def(
        py.init<const:string:ref, const:std.vector<Node>:ref, const:SourceLoc:ref>(),
        py.arg("op"), py.arg("args"), py.arg("source") = SourceLoc())

    py.class_<Call.class, Call:mut>(m, "Call", node).def(
        py.init<Node, const:std.vector<Node>:ref, const:SourceLoc:ref>(),
        py.arg("func"), py.arg("args"), py.arg("source") = SourceLoc()).def_readwrite(
        "is_one_liner_if", &Call.is_one_liner_if)

    py.class_<ArrayAccess.class, ArrayAccess:mut>(m, "ArrayAccess", node).def(
        py.init<Node, const:std.vector<Node>:ref, const:SourceLoc:ref>(),
        py.arg("func"), py.arg("args"), py.arg("source") = SourceLoc())

    py.class_<BracedCall.class, BracedCall:mut>(m, "BracedCall", node).def(
        py.init<Node, const:std.vector<Node>:ref, const:SourceLoc:ref>(),
        py.arg("func"), py.arg("args"), py.arg("source") = SourceLoc())

    py.class_<Template.class, Template:mut>(m, "Template", node).def(
        py.init<Node, const:std.vector<Node>:ref, const:SourceLoc:ref>(),
        py.arg("func"), py.arg("args"), py.arg("source") = SourceLoc())

    py.class_<Identifier.class, Identifier:mut>(m, "Identifier", node).def(
        py.init<const:string:ref, const:SourceLoc:ref>(),
        py.arg("name"), py.arg("source") = SourceLoc())

    py.class_<StringLiteral.class, StringLiteral:mut>(m, "StringLiteral", node).def(
        py.init<const:string:ref, Identifier, Identifier, const:SourceLoc:ref>(),
        py.arg("str"), py.arg("prefix"), py.arg("suffix"), py.arg("source") = SourceLoc()).def_readonly(
        "str", &StringLiteral.str).def_readwrite(
        "prefix", &StringLiteral.prefix).def_readwrite(
        "suffix", &StringLiteral.suffix).def(
        "escaped", &StringLiteral.escaped)

    py.class_<IntegerLiteral.class, IntegerLiteral:mut>(m, "IntegerLiteral", node).def(
        py.init<const:string:ref, Identifier, const:SourceLoc:ref>(),
        py.arg("integer_string"), py.arg("suffix"), py.arg("source") = SourceLoc()).def_readonly(
        "integer_string", &IntegerLiteral.integer_string).def_readonly(
        "suffix", &IntegerLiteral.suffix)

    py.class_<FloatLiteral.class, FloatLiteral:mut>(m, "FloatLiteral", node).def(
        py.init<const:string:ref, Identifier, const:SourceLoc:ref>(),
        py.arg("float_string"), py.arg("suffix"), py.arg("source") = SourceLoc()).def_readonly(
        "float_string", &FloatLiteral.float_string).def_readonly(
        "suffix", &FloatLiteral.suffix)

    list_like: mut = py.class_<ListLike_.class, ListLike_:mut>(m, "ListLike_", node)

    py.class_<ListLiteral.class, ListLiteral:mut>(m, "ListLiteral", list_like).def(
        py.init<const:std.vector<Node>:ref, const:SourceLoc:ref>(), py.arg("args"), py.arg("source") = SourceLoc())

    py.class_<TupleLiteral.class, TupleLiteral:mut>(m, "TupleLiteral", list_like).def(
        py.init<const:std.vector<Node>:ref, const:SourceLoc:ref>(), py.arg("args"), py.arg("source") = SourceLoc())

    py.class_<BracedLiteral.class, BracedLiteral:mut>(m, "BracedLiteral", list_like).def(
        py.init<const:std.vector<Node>:ref, const:SourceLoc:ref>(), py.arg("args"), py.arg("source") = SourceLoc())

    block:mut = py.class_<Block.class, Block:mut>(m, "Block", list_like)
    block.def(py.init<const:std.vector<Node>:ref, const:SourceLoc:ref>(), py.arg("args"), py.arg("source") = SourceLoc())

    py.class_<Module.class, Module:mut>(m, "Module", block).def(py.init<const:std.vector<Node>:ref,
        const:SourceLoc:ref>(), py.arg("args"), py.arg("source") = SourceLoc()).def_readwrite(
        "has_main_function", &Module.has_main_function)

    py.class_<RedundantParens.class, RedundantParens:mut>(m, "RedundantParens", node).def(
        py.init<const:std.vector<Node>:ref, const:SourceLoc:ref>(), py.arg("args"), py.arg("source") = SourceLoc())

    py.class_<InfixWrapper_.class, InfixWrapper_:mut>(m, "InfixWrapper_", node).def(
        py.init<const:std.vector<Node>:ref, const:SourceLoc:ref>(), py.arg("args"), py.arg("source") = SourceLoc())

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

    py.class_<FunctionDefinition.class, FunctionDefinition:mut>(m, "FunctionDefinition").def(
        py.init<Node, Identifier>(), py.arg("def_node"), py.arg("function_name")).def_readwrite(
        "def_node", &FunctionDefinition.def_node).def_readwrite(
        "function_name", &FunctionDefinition.function_name).def(
        "__repr__", &FunctionDefinition.repr)

    py.class_<Scope.class, Scope:mut>(m, "Scope").def(
        py.init<>()).def_readwrite(
        "indent", &Scope.indent).def_readwrite(
        "in_function_body", &Scope.in_function_body).def_readwrite(
        "in_function_param_list", &Scope.in_function_param_list).def_readwrite(
        "in_class_body", &Scope.in_class_body).def_readwrite(
        "is_unsafe", &Scope.is_unsafe).def_readwrite(
        "in_decltype", &Scope.in_decltype).def(
        "indent_str", &Scope.indent_str).def(
        "add_variable_definition", &Scope.add_variable_definition, "defined_node"_a, "defining_node"_a).def(
        "add_interface_method", &Scope.add_interface_method).def(
        "add_class_definition", &Scope.add_class_definition).def(
        "add_function_definition", &Scope.add_function_definition).def(
        "lookup_class", &Scope.lookup_class).def(
        "lookup_function", &Scope.lookup_function).def(
        "find_defs", &Scope.find_defs, py.arg("var_node"), py.arg("find_all") = true).def(
        "find_def", &Scope.find_def).def(
        "enter_scope", &Scope.enter_scope).def_property_readonly(
        "parent", &Scope.parent)

    m.def("creates_new_variable_scope", &creates_new_variable_scope)
    m.def("comes_before", &comes_before)

    # this will need its own module - just for testing for now
    m.def("parse_test", &parse_test)

    py.class_<MacroDefinition.class, MacroDefinition:mut>(m, "MacroDefinition").def(
        py.init<Node, Node, std.map<string, Node>>()).def_readonly(
        "defmacro_node", &MacroDefinition.defmacro_node).def_readonly(
        "pattern_node", &MacroDefinition.pattern_node).def_readonly(
        "parameters", &MacroDefinition.parameters).def_readwrite(
        "dll_path", &MacroDefinition.dll_path).def_readwrite(
        "impl_function_name", &MacroDefinition.impl_function_name)

    m.def("macro_matches", &macro_matches)  # only for test code
    m.def("expand_macros", &expand_macros)

    return
)(m)

cpp"}"  # end PYBIND11MODULE

