# vim: syntax=python

cpp'
#include <map>
#include <typeinfo>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
'

py: namespace = pybind11


class (Node:
    func : Node:mut
    args : [Node:mut]
    source : py.tuple  # typing.Tuple[str, int]

    # TODO BUG: func is treated as a Node rather that a Node:mut when the untyped constructor param's type is inferred from the data member type above ie it's a const shared_ptr<const Node> rather than a const shared_ptr<Node>. Bug not present with an autosynthesized constructor so we'll stay with that for now
#    def (init, func, args, source = py.tuple{}:
#        self.func = func
#        self.args = args
#        self.source = source
#    )

    parent : py.object = py.none()  # TODO implement weak (not sure if this will leak when a cycle is created in python code)
    declared_type : Node:mut = None
    scope : py.object = py.none()

    def (repr: virtual:
        # selph : py.object = py.cast(this)
        # classname = std.string(py.str(selph.attr(c"__class__").attr(c"__name__")))  # cool but unnecessary
        classname : std.string = typeid(*this).name()

        args_str : mut = "["
        for (a in self.args:
            args_str += a.repr() + ", "
        )
        args_str += "]"

        return classname + "(" + self.func.repr() + ")(" + args_str + ")"
    ) : std.string

    def (name: virtual:
        return None
    ) : std.optional<std.string>
)


class (Identifier(Node):
    _name : string

    def (init, name, source: py.tuple:
        self._name = name
        super.init(None, [] : Node : mut, source)
    )

    def (repr:
        return self._name
    ) : std.string

    def (name:
        return self._name
    ) : std.optional<std.string>
)


#no:
#defmacro (wild(x) : std.Function = lambda(wild(b)), x, b:
#)
# this might work:
#defmacro (x: std.function = lambda(b), x: Identifier, b:  # b is generic so instance of WildCard. x is a WildCard with stored_type == Integer
#    # should allow either/mix of these
#    return Assign([TypeOp([x, Call(Identifier("decltype"), [b.parent])]), b.parent])
#    return quote(unquote(x) : std.function(decltype(lambda(unquote(b)))) = lambda(unquote(b)))
#)
#
# 'pattern' is unnecessary:
#defmacro (pattern(x: std.function, t) = pattern(lambda(b), l), x: Identifier, b: Node:
#defmacro (x: std.function = pattern(lambda(Wild(b)), l), x: Identifier, l: Call:
#    return quote(unquote(
#)
#
#

# see a macro
# defmacro_node = ...
# compile macro_impl in dll
# MacroDefinition(pattern=defmacro_node.args[0], action=macro_impl)
#
#def matches(x, y) -> :
#    if x == y == nullptr:
#        return true, None
#     if isinstance(y, WildCard):
#        if not y.stored_typeid or y.stored_typeid() == typeid(x)
#            return true, {y : x}
#        else:
#            return false, None
#    if typeid(x) != typeid(y):    # ugly
#        return false, None
#    if y._is_wildcard:  # ugly (especially in combination with typdid)
#        return true # or the match? {y : x}
#    if len(x.args) != len(y.args):
#        return false, None
#    if len(x.args) == 0 and x.func == None:
#        return x.repr() == y.repr(), None  # ugly
#    submatches = {}
#    for i in range(len(x.args)):
#        m = matches(x[i], y[i])
#         if not m:
#           return false, None
#         submatches.extend(m)
#     m = matches(x.func, y.func):
#     if not m:
#        return false, None
#    submatches.extend(m)
#    return true, submatches
#
#
#       
#
# expansion:
# have a node
# for pattern, action in macro_definitions:
#     if match_dict := matches(node, pattern):
#         node = macro_trampoline(action, match_dict)
#         #node = action(match_dict)
#
# def (macro_action1, match_dict:
#    x = match_dict["x"]
#    y = match_dict["y"]
#
#    return ...
# )
#
# def (macro_trampoline, action_ptr, match_dict:
#     return *action_ptr(match_dict)
#)

def (example_macro_body_workaround_no_fptr_syntax_yet, matches: std.map<string, Node:mut>:
    return None
) : Node:mut

# this should probably take an index into an already dlsymed table of fptrs
def (macro_trampoline, fptr : uintptr_t, matches: std.map<string, Node:mut>:
    # writing a wrapper type for pybind11 around the correct function pointer would be better (fine for now)
    f = reinterpret_cast<decltype(&example_macro_body_workaround_no_fptr_syntax_yet)>(fptr)
    #f2 = reinterpret_cast<decltype(+lambda(matches:std.map<string, Node:mut>, None): Node:mut)>(fptr)   # TODO post-parse hacks for typed lambda only work for immediately invoked lambda aka Call node (not needed for assign case due to lower precedence =). debatable if needs fix for this case?: codegen.CodeGenError: ('unexpected typed construct', UnOp(+)([lambda(matches,Block((return : None)))]))
    #f2 = reinterpret_cast<decltype(+(lambda(matches:std.map<string, Node:mut>, None): Node:mut))>(fptr)  # extra parenthese due to + : precedence (this should work)
    # ^ TODO lambda inside decltype and on rhs of TypeOp (so no attached Scope currently...) results in capture bug with the param somehow ending up in capture list (maybe param not used also part of bug). TODO TypeOp rhs nodes still need an attached scope
    #static_assert(std.is_same_v<decltype(f), decltype(f2)>)
    return (*f)(matches)
)

cpp'
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<Node>>);
PYBIND11_MAKE_OPAQUE(std::map<std::string, std::shared_ptr<Node>>);
PYBIND11_MODULE(abstractsyntaxtree, m) {

    // This would be the sensible thing to do but we are going to write the below in ceto as a torture test:

    //py::bind_vector<std::vector<std::shared_ptr<Node>>>(m, "vector_node");
    //
    //py::class_<Node, std::shared_ptr<Node>> node(m, "Node");
    //node.def("repr", &Node::repr)
    //    .def("name", &Node::name)
    //    .def_readwrite("func", &Node::func)
    //    .def_readwrite("args", &Node::args);
    //
    //py::class_<Identifier, std::shared_ptr<Identifier>>(m, "Identifier", node)
    //    .def(py::init<const std::string &>())
    //    .def("repr", &Identifier::repr)
    //    .def("name", &Identifier::name);
    //
    //m.def("printid", &printid, "A function that prints an id");
//}
'

# More or less equivalent to the above commented c++:

# trick transpiler into local variable context (TODO add 'localscope' blocks then ban non-constexpr global lambdas entirely)
lambda(m: mut:auto:rref:  # TODO lambda params are now naively const by default (hence need for 'mut'). However, const auto&& pretty much makes no sense so maybe anything with 'rref' should be an exception to const by default logic

    #py::bind_vector<[Node:mut]>(m, c"VectorNode")  # this should work but codegen for template params as types needs fix (or maybe force type context with a leading unary ':')
    py.bind_vector<std.vector<Node:mut>>(m, c"VectorNode")
    py.bind_map<std.map<std.string, Node:mut>>(m, c"MapStringNode") #, py.module_local(false))   # requires you to create an explicit d = MapStringNode() on python side

    # TODO Node::class
    node : mut = py.class_<std.type_identity_t<Node:mut>::element_type, Node:mut>(m, c"Node").def_readwrite(
        c"func", &Node.func).def_readwrite(
        c"args", &Node.args).def_readwrite(
        c"parent", &Node.parent).def_readwrite(
        c"declared_type", &Node.declared_type).def_readwrite(
        c"scope", &Node.scope).def_readwrite(
        c"source", &Node.source).def(
        c"__repr__", &Node.repr).def(
        c"name", &Node.name)

    py.class_<std.type_identity_t<Identifier:mut>::element_type, Identifier:mut>(m, c"Identifier", node).def(
        py.init<const:string:ref, py.tuple>())

    #m.def(c"printid", &printid, c"A function that prints an id")
    m.def(c"macro_trampoline", &macro_trampoline, c"macro trampoline")

    return
)(m)

cpp"}"  # end PYBIND11MODULE
