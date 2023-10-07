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
    func: Node
    args: [Node]
    source: py.tuple  # typing.Tuple[str, int]

    def (init, func, args, source = py.tuple{}:
        self.func = func
        self.args = args
        self.source = source
    )

    declared_type: Node = None
    scope: py.object = py.none()
    _parent: Node:weak = {}

    def (repr: virtual:
        # selph : py.object = py.cast(this)
        # classname = std.string(py.str(selph.attr(c"__class__").attr(c"__name__")))  # cool but unnecessary
        classname : std.string = typeid(*this).name()
        csv = join(self.args, lambda(a, a.repr()), ", ")
        return classname + "(" + self.func.repr() + ")([" + csv + "])"
    ) : std.string

    def (name: virtual:
        return std.nullopt
    ) : std.optional<std.string>

    def (parent: virtual:
        return self._parent.lock()
    ) : Node

    def (set_parent: virtual:mut, p: Node:
        self._parent = p
    )
)

class (UnOp(Node):
    op : std.string

    def (init, op, args:[Node], source=py.tuple{}:
        self.op = op
        super.init(None, args, source)
    )

    def (repr:
        return "(" +  self.op + " " + self.args[0].repr() + ")"
    ) : std.string
)

class (LeftAssociativeUnOp(Node):
    op : std.string

    def (init, op, args:[Node], source=py.tuple{}:
        self.op = op
        super.init(None, args, source)
    )

    def (repr:
        return "(" + self.args[0].repr() + " " + self.op + ")"
    ) : std.string
)

class (BinOp(Node):
    op : std.string

    def (init, op, args:[Node], source=py.tuple{}:
        self.op = op
        super.init(None, args, source)
    )

    def (lhs:
        return self.args[0]
    )

    def (rhs:
        return self.args[1]
    )

    def (repr:
        return "(" + self.lhs().repr() + " " + self.op + " " + self.rhs().repr() + ")"
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

class (NamedParameter(Assign):
    def (repr:
        return "NamedParameter(" + join(self.args, lambda(a, a.repr()), ", ")  + ")"
    ) : std.string
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

#class (IntegerLiteral(Node):
#    integer : py.object
#
#    def (init, integer, source = py.tuple{}:
#        self.integer = integer
#        super.init(None, [] : Node, source)
#    )
#
#    def (repr:
#        return std.string(py.str(self.integer))
#    ) : std.string
#)


# User Ingmar
# https://stackoverflow.com/questions/2896600/how-to-replace-all-occurrences-of-a-character-in-string/29752943#29752943
def (string_replace, source: string, from: string, to: string:
    new_string : mut = std.string()
    new_string.reserve(source.length())  # avoids a few memory allocations

    last_pos : mut:std.string.size_type = 0  # TODO just string.size_type should also generate std::string::size_type
    find_pos : mut:std.string.size_type = 0

    while (std.string.npos != (find_pos = source.find(from, last_pos)):
        new_string.append(source, last_pos, find_pos - last_pos)
        new_string += to
        last_pos = find_pos + from.length()
    )

    new_string.append(source, last_pos, source.length() - last_pos)  # better than new_string += source.substr(last_pos) to avoid creating temporary string [as substr() does]. – tav

    return new_string  # clang and g++ -O3 produce less code returning by value than taking source by mut:ref as in answer url
)


class (StringLiteral(Node):
    str : string
    prefix : Identifier
    suffix : Identifier

    def (init, str, prefix: Identifier = None, suffix: Identifier = None, source = py.tuple{}:
        self.str = str
        self.prefix = prefix
        self.suffix = suffix
        super.init(None, [] : Node, source)
    )

    def (escaped:
        s : mut = string_replace(self.str, "\n", "\\n")
        s = string_replace(s, '"', '\"')
        s = '"' + s + '"'
        return s
    )

    def (repr:
        return if (self.prefix:
            self.prefix.name().value()
        else:
            ""
        ) + self.escaped() + if (self.suffix:
            self.suffix.name().value()
        else:
            ""
        )
    ) : string
)

class (IntegerLiteral(Node):
    integer_string : std.string
    suffix : Identifier

    def (init, integer_string, suffix: Identifier = None, source = py.tuple{}:
        self.integer_string = integer_string
        self.suffix = suffix
        super.init(None, {}, source)
    )

    def (repr:
        return self.integer_string + if (self.suffix: self.suffix.name().value() else: "")
    ) : std.string
)

class (FloatLiteral(Node):
    float_string : std.string
    suffix : Identifier

    def (init, float_string, suffix : Identifier, source = py.tuple{}:
        self.float_string = float_string
        self.suffix = suffix
        super.init(None, {}, source)
    )

    def (repr:
        return self.float_string + if (self.suffix: self.suffix.name().value() else: "")
    ) : std.string
)

class (ListLike_(Node):
    def (init, args: [Node], source = py.tuple{}:
        super.init(None, args, source)
    )

    def (repr:
        classname = std.string(typeid(*this).name())
        return classname + "(" + join(self.args, lambda (a, a.repr()), ", ") + ")"
    ) : std.string
)

class (ListLiteral(ListLike_):
    pass
)

class (TupleLiteral(ListLike_):
    pass
)

class (BracedLiteral(ListLike_):
    pass
)

class (Block(ListLike_):
    pass
)

class (Module(Block):
    has_main_function = false
)

class (RedundantParens(Node):
    def (init, args: [Node], source = py.tuple{}:
        super.init(None, args, source)
    )

    def (repr:
        classname = std.string(typeid(*this).name())
        return classname + "(" + join(self.args, lambda (a, a.repr()), ", ") + ")"
    ) : std.string
)

class (InfixWrapper_(Node):
    def (init, args: [Node], source = py.tuple{}:
        super.init(None, args, source)
    )

    def (repr:
        classname = std.string(typeid(*this).name())
        return classname + "(" + join(self.args, lambda (a, a.repr()), ", ") + ")"
    ) : std.string
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

#defmacro (x: std.function = lambda(b...), x : Identifier, b:  # b is generic but it's using in a ... expression so it's a vector of WildCard. x is a WildInteger or maybe just WildCard with stored_type == Integer
#    return quote(unquote(x) : std.function(decltype(lambda(unquote(b)))) = lambda(unquote(b)))  # should unquote auto unpack a vector of Nodes?
#    return quote(unquote(x) : std.function(decltype(lambda(unpack(b)))) = lambda(unpack(b)))  # maybe unpack is clearer or at least easier to implement
#    return quote(unquote(x) : std.function(decltype(lambda(unquote(b...)))) = lambda(unquote(b...)))  # more clever if a bit more confusing and C++y
#)
# ^ although this would preclude a macro that modifies ... expressions? alternative:
#defmacro (x: std.function = lambda(b), x : Identifier, b:  # b is generic but it's fed to 'unpack' so it's a vector of WildCard. x is a WildInteger or maybe just WildCard with stored_type == Integer
#    return quote(unquote(x) : std.function(decltype(lambda(unpack(b)))) = lambda(unpack(b)))
#)
# better:
#defmacro (x: std.function = lambda(b), x: Identifier, b: ...:  # b is a vector of WildCard. x is a WildInteger or maybe just WildCard with stored_type == Integer
#    return quote(unquote(x) : std.function(decltype(lambda(unpack(b)))) = lambda(unpack(b)))  # unpack distinct from unquote is better in case we can't determine at transpile time if b is a vector
#)

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

#PYBIND11_MAKE_OPAQUE(std.vector<Node>)
#PYBIND11_MAKE_OPAQUE(std.map<string, Node>)

cpp'
PYBIND11_MODULE(_abstractsyntaxtree, m) {
'

# trick transpiler into local variable context (TODO add 'scope(Block([]))' then ban non-constexpr global lambdas entirely)
lambda(m: mut:auto:rref:  # TODO lambda params are now naively const by default (hence need for 'mut'). However, const auto&& pretty much makes no sense so maybe anything with 'rref' should be an exception to const by default logic

    #py::bind_vector<[Node]>(m, c"VectorNode")  # this should work but codegen for template params as types needs fix (also maybe force type context with a leading unary ':')
    py.bind_vector<std.vector<Node>>(m, c"NodeVector")
    py.bind_map<std.map<std.string, Node>>(m, c"StringNodeMap")

    # Node:mut even though we're using Node aka Node:const (std::shared_ptr<const Node>) elsewhere - see https://github.com/pybind/pybind11/issues/131
    node : mut = py.class_<Node.class, Node:mut>(m, c"Node").def_readwrite(
        c"func", &Node.func).def_readwrite(
        c"args", &Node.args).def_readwrite(
        c"declared_type", &Node.declared_type).def_readwrite(
        c"scope", &Node.scope).def_readwrite(
        c"source", &Node.source).def(
        c"__repr__", &Node.repr).def_property_readonly(
        c"name", &Node.name).def_property(
        c"parent", &Node.parent, &Node.set_parent)

    py.class_<UnOp.class, UnOp:mut>(m, c"UnOp", node).def(
        py.init<const:string:ref, std.vector<Node>, py.tuple>()).def_readwrite(
        c"op", &UnOp.op)

    py.class_<LeftAssociativeUnOp.class, LeftAssociativeUnOp:mut>(m, c"LeftAssociativeUnOp", node).def(
        py.init<const:string:ref, std.vector<Node>, py.tuple>()) .def_readwrite(
        c"op", &LeftAssociativeUnOp.op)

    binop : mut = py.class_<BinOp.class, BinOp:mut>(m, c"BinOp", node)
    binop.def(py.init<const:string:ref, std.vector<Node>, py.tuple>()).def_readwrite(
        c"op", &BinOp.op).def_property_readonly(
        c"lhs", &BinOp.lhs).def_property_readonly(
        c"rhs", &BinOp.rhs)

    typeop: mut = py.class_<TypeOp.class, TypeOp:mut>(m, c"TypeOp", binop)
    typeop.def(py.init<const:string:ref, std.vector<Node>, py.tuple>())

    py.class_<SyntaxTypeOp.class, SyntaxTypeOp:mut>(m, c"SyntaxTypeOp", typeop).def(
        py.init<const:string:ref, std.vector<Node>, py.tuple>())

    py.class_<AttributeAccess.class, AttributeAccess:mut>(m, c"AttributeAccess", binop).def(
        py.init<const:string:ref, std.vector<Node>, py.tuple>())

    py.class_<ArrowOp.class, ArrowOp:mut>(m, c"ArrowOp", binop).def(
        py.init<const:string:ref, std.vector<Node>, py.tuple>())

    py.class_<ScopeResolution.class, ScopeResolution:mut>(m, c"ScopeResolution", binop).def(
        py.init<const:string:ref, std.vector<Node>, py.tuple>())

    assign:mut = py.class_<Assign.class, Assign:mut>(m, c"Assign", binop)
    assign.def(py.init<const:string:ref, std.vector<Node>, py.tuple>())

    py.class_<NamedParameter.class, NamedParameter:mut>(m, c"NamedParameter", assign).def(
        py.init<const:string:ref, std.vector<Node>, py.tuple>())

    py.class_<Call.class, Call:mut>(m, c"Call", node).def(
        py.init<Node, std.vector<Node>, py.tuple>())

    py.class_<ArrayAccess.class, ArrayAccess:mut>(m, c"ArrayAccess", node).def(
        py.init<Node, std.vector<Node>, py.tuple>())

    py.class_<BracedCall.class, BracedCall:mut>(m, c"BracedCall", node).def(
        py.init<Node, std.vector<Node>, py.tuple>())

    py.class_<Template.class, Template:mut>(m, c"Template", node).def(
        py.init<Node, std.vector<Node>, py.tuple>())

    py.class_<Identifier.class, Identifier:mut>(m, c"Identifier", node).def(
        py.init<const:string:ref, py.tuple>())

    py.class_<StringLiteral.class, StringLiteral:mut>(m, c"StringLiteral", node).def(
        py.init<const:string:ref, Identifier, Identifier, py.tuple>()).def_readonly(
        c"str", &StringLiteral.str).def_readonly(
        c"prefix", &StringLiteral.prefix).def_readonly(
        c"suffix", &StringLiteral.suffix)

    py.class_<IntegerLiteral.class, IntegerLiteral:mut>(m, c"IntegerLiteral", node).def(
        py.init<const:string:ref, Identifier, py.tuple>()).def_readonly(
        c"integer_string", &IntegerLiteral.integer_string).def_readonly(
        c"suffix", &IntegerLiteral.suffix)

    py.class_<FloatLiteral.class, FloatLiteral:mut>(m, c"FloatLiteral", node).def(
        py.init<const:string:ref, Identifier, py.tuple>()).def_readonly(
        c"float_string", &FloatLiteral.float_string).def_readonly(
        c"suffix", &FloatLiteral.suffix)

    list_like: mut = py.class_<ListLike_.class, ListLike_:mut>(m, c"ListLike_", node)

    py.class_<ListLiteral.class, ListLiteral:mut>(m, c"ListLiteral", list_like).def(
        py.init<std.vector<Node>, py.tuple>())

    py.class_<TupleLiteral.class, TupleLiteral:mut>(m, c"TupleLiteral", list_like).def(
        py.init<std.vector<Node>, py.tuple>())

    py.class_<BracedLiteral.class, BracedLiteral:mut>(m, c"BracedLiteral", list_like).def(
        py.init<std.vector<Node>, py.tuple>())

    block:mut = py.class_<Block.class, Block:mut>(m, c"Block", list_like)
    block.def(py.init<std.vector<Node>, py.tuple>())

    py.class_<Module.class, Module:mut>(m, c"Module", block).def(
        py.init<std.vector<Node>, py.tuple>()).def_readwrite(
        c"has_main_function", &Module.has_main_function)

    py.class_<RedundantParens.class, RedundantParens:mut>(m, c"RedundantParens", node).def(
        py.init<std.vector<Node>, py.tuple>())

    py.class_<InfixWrapper_.class, InfixWrapper_:mut>(m, c"InfixWrapper_", node).def(
        py.init<std.vector<Node>, py.tuple>())

    m.def(c"macro_trampoline", &macro_trampoline, c"macro trampoline")

    return
)(m)

cpp"}"  # end PYBIND11MODULE

