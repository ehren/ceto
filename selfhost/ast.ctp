# vim: syntax=python

cpp'
#include <map>
#include <typeinfo>
#include <numeric>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
'

py: namespace = pybind11


def (join, v, to_string, sep="":
    if (v.empty():
        return ""
    )
    return std.accumulate(v.cbegin() + 1, v.cend(), to_string(v[0]),
        lambda[&to_string, &sep] (a, el, a + sep + to_string(el)))
)


class (Node:
    func : Node
    args : [Node]
    source : py.tuple  # typing.Tuple[str, int]

    def (init, func, args, source = py.tuple{}:
        self.func = func
        self.args = args
        self.source = source
    )

    parent : py.object = py.none()  # TODO implement weak (not sure if this will leak when a cycle is created in python code)
    declared_type : Node = None
    scope : py.object = py.none()

    def (repr: virtual:
        # selph : py.object = py.cast(this)
        # classname = std.string(py.str(selph.attr(c"__class__").attr(c"__name__")))  # cool but unnecessary
        classname : std.string = typeid(*this).name()
        csv = join(self.args, lambda(a, a.repr()), ", ")
        return classname + "(" + self.func.repr() + ")([" + csv + "])"
    ) : std.string

    def (name: virtual:
        return None
    ) : std.optional<std.string>
)

class (UnOp(Node):
    pass
)

class (LeftAssociativeUnOp(Node):
    pass
)

class (BinOp(Node):

    def (lhs:
        return self.args[0]
    )

    def (rhs:
        return self.args[1]
    )

    def (repr:
        return join([self.lhs(), self.func, self.rhs()], lambda(a, a.repr()), " ")
    ) : std.string
)

class (TypeOp(BinOp):
    pass
)

class (SyntaxTypeOp(TypeOp):
    pass
)

class (AttributeAccess(BinOp):

    def (repr:
        return self.lhs().repr() + "." + self.rhs().repr()
    ) : std.string
)

class (ArrowOp(BinOp):
    pass
)

class (ScopeResolution(BinOp):
    pass
)

class (Assign(BinOp):
    pass
)

class (Identifier(Node):
    _name : string

    def (init, name, source = py.tuple{}:
        self._name = name
        super.init(None, [] : Node, source)
    )

    def (repr:
        return self._name
    ) : std.string

    def (name:
        return self._name
    ) : std.optional<std.string>
)

class (Call(Node):
    def (repr:
        csv = join(self.args, lambda (a, a.repr()), ", ")
        return self.func.repr() + "(" + csv + ")"
    ) : std.string
)

class (ArrayAccess(Node):
    def (repr:
        csv = join(self.args, lambda (a, a.repr()), ", ")
        return self.func.repr() + "[" + csv + "]"
    ) : std.string
)

class (BracedCall(Node):
    def (repr:
        csv = join(self.args, lambda (a, a.repr()), ", ")
        return self.func.repr() + "{" + csv + "}"
    ) : std.string
)

class (Template(Node):
    def (repr:
        csv = join(self.args, lambda (a, a.repr()), ", ")
        return self.func.repr() + "<" + csv + ">"
    ) : std.string
)

class (IntegerLiteral(Node):
    integer : py.object

    def (init, integer, source = py.tuple{}:
        self.integer = integer
        super.init(None, [] : Node, source)
    )

    def (repr:
        return std.string(py.str(self.integer))
    ) : std.string
)


# https://stackoverflow.com/questions/2896600/how-to-replace-all-occurrences-of-a-character-in-string/24315631#24315631
#std::string ReplaceAll(std::string str, const std::string& from, const std::string& to) {
#    size_t start_pos = 0;
#    while((start_pos = str.find(from, start_pos)) != std::string::npos) {
#        str.replace(start_pos, from.length(), to);
#        start_pos += to.length(); // Handles case where 'to' is a substring of 'from'
#    }
#    return str;
#}


def (string_replace, str : string, from : string, to : string:
    start_pos: mut:size_t = 0
    res : mut = str  # string passed by const ref by default
    while ((start_pos = res.find(from, start_pos)) != std.string.npos:  # TODO just 'string.npos' (or string::npos) should be possible if you can write just 'string' (to codegen std::string)
        res.replace(start_pos, from.length(), to)
        start_pos += to.length()  # // Handles case where 'to' is a substring of 'from'
    )
    return res
)


#class (StringLiteral(Node):
#    string : std.string  # this is weird
#
#    def (repr:
#        escaped = self.escaped()
#        if self.prefix:
#            escaped = self.prefix.name + escaped
#        if self.suffix:
#            escaped += self.suffix.name
#        return escaped
#    )
#
#    def escaped(self):
#        escaped = self.string.replace("\n", r"\n")
#        escaped = '"' + escaped + '"'
#        return escaped
#    )
#
#    def __init__(self, string, prefix, suffix, source):
#        self.string = string
#        self.prefix = prefix
#        self.suffix = suffix
#        super().__init__(None, [], source)
#    )
#)

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

def (example_macro_body_workaround_no_fptr_syntax_yet, matches: std.map<string, Node>:
    return None
) : Node

# this should probably take an index into an already dlsymed table of fptrs
def (macro_trampoline, fptr : uintptr_t, matches: std.map<string, Node>:
    # writing a wrapper type for pybind11 around the correct function pointer would be better (fine for now)
    f = reinterpret_cast<decltype(&example_macro_body_workaround_no_fptr_syntax_yet)>(fptr)
    #f2 = reinterpret_cast<decltype(+lambda(matches:std.map<string, Node:mut>, None): Node:mut)>(fptr)   # TODO post-parse hacks for typed lambda only work for immediately invoked lambda aka Call node (not needed for assign case due to lower precedence =). debatable if needs fix for this case?: codegen.CodeGenError: ('unexpected typed construct', UnOp(+)([lambda(matches,Block((return : None)))]))
    #f2 = reinterpret_cast<decltype(+(lambda(matches:std.map<string, Node:mut>, None): Node:mut))>(fptr)  # extra parenthese due to + : precedence (this should work)
    # ^ TODO lambda inside decltype and on rhs of TypeOp (so no attached Scope currently...) results in capture bug with the param somehow ending up in capture list (maybe param not used also part of bug). TODO TypeOp rhs nodes still need an attached scope
    #static_assert(std.is_same_v<decltype(f), decltype(f2)>)
    return (*f)(matches)
)

cpp'
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<const Node>>);
PYBIND11_MAKE_OPAQUE(std::map<std::string, std::shared_ptr<const Node>>);
PYBIND11_MODULE(_abstractsyntaxtree, m) {

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
    py.bind_vector<std.vector<Node>>(m, c"NodeVector")
    py.bind_map<std.map<std.string, Node>>(m, c"StringNodeMap") #, py.module_local(false))   # requires you to create an explicit d = MapStringNode() on python side

    # Node:mut even though we're using Node aka Node:const (std::shared_ptr<const Node>) elsewhere - see https://github.com/pybind/pybind11/issues/131
    node : mut = py.class_<Node.class, Node:mut>(m, c"Node").def_readwrite(
        c"func", &Node.func).def_readwrite(
        c"args", &Node.args).def_readwrite(
        c"parent", &Node.parent).def_readwrite(
        c"declared_type", &Node.declared_type).def_readwrite(
        c"scope", &Node.scope).def_readwrite(
        c"source", &Node.source).def(
        c"__repr__", &Node.repr).def(
        c"name", &Node.name)

    py.class_<Identifier.class, Identifier:mut>(m, c"Identifier", node).def(
        py.init<const:string:ref, py.tuple>())

    #m.def(c"printid", &printid, c"A function that prints an id")
    m.def(c"macro_trampoline", &macro_trampoline, c"macro trampoline")

    return
)(m)

cpp"}"  # end PYBIND11MODULE

