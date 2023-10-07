
#include <string>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <sstream>
#include <functional>
#include <cassert>
#include <compare> // for <=>
#include <thread>
#include <optional>

//#include <concepts>
//#include <ranges>
//#include <numeric>


#include "ceto.h"


#include <map>
#include <typeinfo>
#include <numeric>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
;
namespace py = pybind11;
    template <typename T1, typename T2>
auto join(const T1& v, const T2& to_string, const decltype(std::string {""})&  sep = std::string {""}) -> auto {
if (ceto::mado(v)->empty()) {
            return std::string {""};
        }
        return std::accumulate(ceto::mado(v)->cbegin() + 1, ceto::mado(v)->cend(), to_string(ceto::maybe_bounds_check_access(v,0)), [&to_string, &sep](const auto &a, const auto &el) {
                if constexpr (!std::is_void_v<decltype(((a + sep) + to_string(el)))>) { return ((a + sep) + to_string(el)); } else { static_cast<void>(((a + sep) + to_string(el))); };
                });
    }

struct Node : ceto::shared_object {

    std::shared_ptr<const Node> func;

    std::vector<std::shared_ptr<const Node>> args;

    py::tuple source;

    std::weak_ptr<const Node> parent = {};

    std::shared_ptr<const Node> declared_type = nullptr; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(nullptr), std::remove_cvref_t<decltype(declared_type)>>);

    py::object scope = py::none(); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(py::none()), std::remove_cvref_t<decltype(scope)>>);

         virtual inline auto repr() const -> std::string {
            const std::string classname = ceto::mado(typeid((*this)))->name(); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(ceto::mado(typeid((*this)))->name()), std::remove_cvref_t<decltype(classname)>>);
            const auto csv = join(this -> args, [](const auto &a) {
                    if constexpr (!std::is_void_v<decltype(ceto::mado(a)->repr())>) { return ceto::mado(a)->repr(); } else { static_cast<void>(ceto::mado(a)->repr()); };
                    }, std::string {", "});
            return (((((classname + std::string {"("}) + ceto::mado(this -> func)->repr()) + std::string {")(["}) + csv) + std::string {"])"});
        }

         virtual inline auto name() const -> std::optional<std::string> {
            return std::nullopt;
        }

    explicit Node(const std::shared_ptr<const Node>&  func, const std::vector<std::shared_ptr<const Node>>&  args, const decltype(py::tuple{}) source = py::tuple{}) : func(func), args(args), source(source) {
    }

    Node() = delete;

};

struct UnOp : public std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> {

    std::string op;

        inline auto repr() const -> std::string {
            return ((((std::string {"("} + (this -> op)) + std::string {" "}) + ceto::mado(ceto::maybe_bounds_check_access(this -> args,0))->repr()) + std::string {")"});
        }

    explicit UnOp(const std::string&  op, const std::vector<std::shared_ptr<const Node>>&  args, const decltype(py::tuple{}) source = py::tuple{}) : std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> (nullptr, args, source), op(op) {
    }

    UnOp() = delete;

};

struct LeftAssociativeUnOp : public std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> {

    std::string op;

        inline auto repr() const -> std::string {
            return ((((std::string {"("} + ceto::mado(ceto::maybe_bounds_check_access(this -> args,0))->repr()) + std::string {" "}) + (this -> op)) + std::string {")"});
        }

    explicit LeftAssociativeUnOp(const std::string&  op, const std::vector<std::shared_ptr<const Node>>&  args, const decltype(py::tuple{}) source = py::tuple{}) : std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> (nullptr, args, source), op(op) {
    }

    LeftAssociativeUnOp() = delete;

};

struct BinOp : public std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> {

    std::string op;

        inline auto lhs() const -> auto {
            return ceto::maybe_bounds_check_access(this -> args,0);
        }

        inline auto rhs() const -> auto {
            return ceto::maybe_bounds_check_access(this -> args,1);
        }

        inline auto repr() const -> std::string {
            return ((((((std::string {"("} + ceto::mado(this -> lhs())->repr()) + std::string {" "}) + (this -> op)) + std::string {" "}) + ceto::mado(this -> rhs())->repr()) + std::string {")"});
        }

    explicit BinOp(const std::string&  op, const std::vector<std::shared_ptr<const Node>>&  args, const decltype(py::tuple{}) source = py::tuple{}) : std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> (nullptr, args, source), op(op) {
    }

    BinOp() = delete;

};

struct TypeOp : public BinOp {

using BinOp::BinOp;

};

struct SyntaxTypeOp : public TypeOp {

using TypeOp::TypeOp;

};

struct AttributeAccess : public BinOp {

using BinOp::BinOp;

        inline auto repr() const -> std::string {
            return ((ceto::mado(this -> lhs())->repr() + std::string {"."}) + ceto::mado(this -> rhs())->repr());
        }

};

struct ArrowOp : public BinOp {

using BinOp::BinOp;

};

struct ScopeResolution : public BinOp {

using BinOp::BinOp;

};

struct Assign : public BinOp {

using BinOp::BinOp;

};

struct NamedParameter : public Assign {

using Assign::Assign;

        inline auto repr() const -> std::string {
            return ((std::string {"NamedParameter("} + join(this -> args, [](const auto &a) {
                    if constexpr (!std::is_void_v<decltype(ceto::mado(a)->repr())>) { return ceto::mado(a)->repr(); } else { static_cast<void>(ceto::mado(a)->repr()); };
                    }, std::string {", "})) + std::string {")"});
        }

};

struct Identifier : public std::type_identity_t<decltype(Node(nullptr, std::vector<std::shared_ptr<const Node>>{}, std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> {

    std::string _name;

        inline auto repr() const -> std::string {
            return (this -> _name);
        }

        inline auto name() const -> std::optional<std::string> {
            return (this -> _name);
        }

    explicit Identifier(const std::string&  name, const decltype(py::tuple{}) source = py::tuple{}) : std::type_identity_t<decltype(Node(nullptr, std::vector<std::shared_ptr<const Node>>{}, std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> (nullptr, std::vector<std::shared_ptr<const Node>>{}, source), _name(name) {
    }

    Identifier() = delete;

};

struct Call : public Node {

using Node::Node;

        inline auto repr() const -> std::string {
            const auto csv = join(this -> args, [](const auto &a) {
                    if constexpr (!std::is_void_v<decltype(ceto::mado(a)->repr())>) { return ceto::mado(a)->repr(); } else { static_cast<void>(ceto::mado(a)->repr()); };
                    }, std::string {", "});
            return (((ceto::mado(this -> func)->repr() + std::string {"("}) + csv) + std::string {")"});
        }

};

struct ArrayAccess : public Node {

using Node::Node;

        inline auto repr() const -> std::string {
            const auto csv = join(this -> args, [](const auto &a) {
                    if constexpr (!std::is_void_v<decltype(ceto::mado(a)->repr())>) { return ceto::mado(a)->repr(); } else { static_cast<void>(ceto::mado(a)->repr()); };
                    }, std::string {", "});
            return (((ceto::mado(this -> func)->repr() + std::string {"["}) + csv) + std::string {"]"});
        }

};

struct BracedCall : public Node {

using Node::Node;

        inline auto repr() const -> std::string {
            const auto csv = join(this -> args, [](const auto &a) {
                    if constexpr (!std::is_void_v<decltype(ceto::mado(a)->repr())>) { return ceto::mado(a)->repr(); } else { static_cast<void>(ceto::mado(a)->repr()); };
                    }, std::string {", "});
            return (((ceto::mado(this -> func)->repr() + std::string {"{"}) + csv) + std::string {"}"});
        }

};

struct Template : public Node {

using Node::Node;

        inline auto repr() const -> std::string {
            const auto csv = join(this -> args, [](const auto &a) {
                    if constexpr (!std::is_void_v<decltype(ceto::mado(a)->repr())>) { return ceto::mado(a)->repr(); } else { static_cast<void>(ceto::mado(a)->repr()); };
                    }, std::string {", "});
            return (((ceto::mado(this -> func)->repr() + std::string {"<"}) + csv) + std::string {">"});
        }

};

    inline auto string_replace(const std::string&  source, const std::string&  from, const std::string&  to) -> auto {
        auto new_string { std::string() } ;
        ceto::mado(new_string)->reserve(ceto::mado(source)->length());
        std::string::size_type last_pos { 0 } ; static_assert(std::is_convertible_v<decltype(0), decltype(last_pos)>);
        std::string::size_type find_pos { 0 } ; static_assert(std::is_convertible_v<decltype(0), decltype(find_pos)>);
while (std::string::npos != (find_pos = ceto::mado(source)->find(from, last_pos))) {            ceto::mado(new_string)->append(source, last_pos, find_pos - last_pos);
            new_string += to;
            last_pos = (find_pos + ceto::mado(from)->length());
        }
        ceto::mado(new_string)->append(source, last_pos, ceto::mado(source)->length() - last_pos);
        return new_string;
    }

struct StringLiteral : public std::type_identity_t<decltype(Node(nullptr, std::vector<std::shared_ptr<const Node>>{}, std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> {

    std::string str;

    std::shared_ptr<const Identifier> prefix;

    std::shared_ptr<const Identifier> suffix;

        inline auto escaped() const -> auto {
            auto s { string_replace(this -> str, std::string {"\n"}, std::string {"\\n"}) } ;
            s = string_replace(s, std::string {"\""}, std::string {"\""});
            s = ((std::string {"\""} + s) + std::string {"\""});
            return s;
        }

        inline auto repr() const -> std::string {
            return (([&]() {if (this -> prefix) {
                return ceto::mad(ceto::mado(this -> prefix)->name())->value();
            } else {
                return std::string {""};
            }}()
 + this -> escaped()) + [&]() {if (this -> suffix) {
                return ceto::mad(ceto::mado(this -> suffix)->name())->value();
            } else {
                return std::string {""};
            }}()
);
        }

    explicit StringLiteral(const std::string&  str, const std::shared_ptr<const Identifier>& prefix = nullptr, const std::shared_ptr<const Identifier>& suffix = nullptr, const decltype(py::tuple{}) source = py::tuple{}) : std::type_identity_t<decltype(Node(nullptr, std::vector<std::shared_ptr<const Node>>{}, std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> (nullptr, std::vector<std::shared_ptr<const Node>>{}, source), str(str), prefix(prefix), suffix(suffix) {
    }

    StringLiteral() = delete;

};

struct IntegerLiteral : public std::type_identity_t<decltype(Node(nullptr, {}, std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> {

    std::string integer_string;

    std::shared_ptr<const Identifier> suffix;

        inline auto repr() const -> std::string {
            return ((this -> integer_string) + [&]() {if (this -> suffix) {
                return ceto::mad(ceto::mado(this -> suffix)->name())->value();
            } else {
                return std::string {""};
            }}()
);
        }

    explicit IntegerLiteral(const std::string&  integer_string, const std::shared_ptr<const Identifier>& suffix = nullptr, const decltype(py::tuple{}) source = py::tuple{}) : std::type_identity_t<decltype(Node(nullptr, {}, std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> (nullptr, {}, source), integer_string(integer_string), suffix(suffix) {
    }

    IntegerLiteral() = delete;

};

struct FloatLiteral : public std::type_identity_t<decltype(Node(nullptr, {}, std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> {

    std::string float_string;

    std::shared_ptr<const Identifier> suffix;

    explicit FloatLiteral(const std::string&  float_string, const std::shared_ptr<const Identifier>&  suffix, const decltype(py::tuple{}) source = py::tuple{}) : std::type_identity_t<decltype(Node(nullptr, {}, std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> (nullptr, {}, source), float_string(float_string), suffix(suffix) {
    }

    FloatLiteral() = delete;

};

struct ListLike_ : public std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> {

        inline auto repr() const -> std::string {
            const auto classname = std::string(ceto::mado(typeid((*this)))->name());
            return (((classname + std::string {"("}) + join(this -> args, [](const auto &a) {
                    if constexpr (!std::is_void_v<decltype(ceto::mado(a)->repr())>) { return ceto::mado(a)->repr(); } else { static_cast<void>(ceto::mado(a)->repr()); };
                    }, std::string {", "})) + std::string {")"});
        }

    explicit ListLike_(const std::vector<std::shared_ptr<const Node>>&  args, const decltype(py::tuple{}) source = py::tuple{}) : std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> (nullptr, args, source) {
    }

    ListLike_() = delete;

};

struct ListLiteral : public ListLike_ {

using ListLike_::ListLike_;

};

struct TupleLiteral : public ListLike_ {

using ListLike_::ListLike_;

};

struct BracedLiteral : public ListLike_ {

using ListLike_::ListLike_;

};

struct Block : public ListLike_ {

using ListLike_::ListLike_;

};

struct Module : public Block {

using Block::Block;

    std::remove_cvref_t<decltype(false)> has_main_function = false;

};

struct RedundantParens : public std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> {

        inline auto repr() const -> std::string {
            const auto classname = std::string(ceto::mado(typeid((*this)))->name());
            return (((classname + std::string {"("}) + join(this -> args, [](const auto &a) {
                    if constexpr (!std::is_void_v<decltype(ceto::mado(a)->repr())>) { return ceto::mado(a)->repr(); } else { static_cast<void>(ceto::mado(a)->repr()); };
                    }, std::string {", "})) + std::string {")"});
        }

    explicit RedundantParens(const std::vector<std::shared_ptr<const Node>>&  args, const decltype(py::tuple{}) source = py::tuple{}) : std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>()))> (nullptr, args, source) {
    }

    RedundantParens() = delete;

};

    inline auto example_macro_body_workaround_no_fptr_syntax_yet(const std::map<std::string,std::shared_ptr<const Node>>  matches) -> std::shared_ptr<const Node> {
        return nullptr;
    }

    inline auto macro_trampoline(const uintptr_t  fptr, const std::map<std::string,std::shared_ptr<const Node>>  matches) -> auto {
        const auto f = reinterpret_cast<decltype(&example_macro_body_workaround_no_fptr_syntax_yet)>(fptr);
        return (*f)(matches);
    }

PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<const Node>>);
PYBIND11_MAKE_OPAQUE(std::map<std::string,std::shared_ptr<const Node>>);

PYBIND11_MODULE(_abstractsyntaxtree, m) {
;
[]( auto &&  m) {
        py::bind_vector<std::vector<std::shared_ptr<const Node>>>(m, "NodeVector");
        py::bind_map<std::map<std::string,std::shared_ptr<const Node>>>(m, "StringNodeMap");
        auto node { ceto::mado(ceto::mado(ceto::mado(ceto::mado(ceto::mado(ceto::mado(ceto::mado(ceto::mado(py::class_<Node,std::shared_ptr<Node>>(m, "Node"))->def_readwrite("func", (&Node::func)))->def_readwrite("args", (&Node::args)))->def_readwrite("parent", (&Node::parent)))->def_readwrite("declared_type", (&Node::declared_type)))->def_readwrite("scope", (&Node::scope)))->def_readwrite("source", (&Node::source)))->def("__repr__", (&Node::repr)))->def("name", (&Node::name)) } ;
        ceto::mado(py::class_<UnOp,std::shared_ptr<UnOp>>(m, "UnOp", node))->def(py::init<const std::string &,std::vector<std::shared_ptr<const Node>>,py::tuple>());
        ceto::mado(py::class_<LeftAssociativeUnOp,std::shared_ptr<LeftAssociativeUnOp>>(m, "LeftAssociativeUnOp", node))->def(py::init<const std::string &,std::vector<std::shared_ptr<const Node>>,py::tuple>());
        auto binop { py::class_<BinOp,std::shared_ptr<BinOp>>(m, "BinOp", node) } ;
        ceto::mado(binop)->def(py::init<const std::string &,std::vector<std::shared_ptr<const Node>>,py::tuple>());
        auto typeop { py::class_<TypeOp,std::shared_ptr<TypeOp>>(m, "TypeOp", binop) } ;
        ceto::mado(typeop)->def(py::init<const std::string &,std::vector<std::shared_ptr<const Node>>,py::tuple>());
        ceto::mado(py::class_<SyntaxTypeOp,std::shared_ptr<SyntaxTypeOp>>(m, "SyntaxTypeOp", typeop))->def(py::init<const std::string &,std::vector<std::shared_ptr<const Node>>,py::tuple>());
        ceto::mado(py::class_<AttributeAccess,std::shared_ptr<AttributeAccess>>(m, "AttributeAccess", binop))->def(py::init<const std::string &,std::vector<std::shared_ptr<const Node>>,py::tuple>());
        ceto::mado(py::class_<ArrowOp,std::shared_ptr<ArrowOp>>(m, "ArrowOp", binop))->def(py::init<const std::string &,std::vector<std::shared_ptr<const Node>>,py::tuple>());
        ceto::mado(py::class_<ScopeResolution,std::shared_ptr<ScopeResolution>>(m, "ScopeResolution", binop))->def(py::init<const std::string &,std::vector<std::shared_ptr<const Node>>,py::tuple>());
        auto assign { py::class_<Assign,std::shared_ptr<Assign>>(m, "Assign", binop) } ;
        ceto::mado(assign)->def(py::init<const std::string &,std::vector<std::shared_ptr<const Node>>,py::tuple>());
        ceto::mado(py::class_<NamedParameter,std::shared_ptr<NamedParameter>>(m, "NamedParameter", assign))->def(py::init<const std::string &,std::vector<std::shared_ptr<const Node>>,py::tuple>());
        ceto::mado(py::class_<Call,std::shared_ptr<Call>>(m, "Call", node))->def(py::init<std::shared_ptr<const Node>,std::vector<std::shared_ptr<const Node>>,py::tuple>());
        ceto::mado(py::class_<ArrayAccess,std::shared_ptr<ArrayAccess>>(m, "ArrayAccess", node))->def(py::init<std::shared_ptr<const Node>,std::vector<std::shared_ptr<const Node>>,py::tuple>());
        ceto::mado(py::class_<BracedCall,std::shared_ptr<BracedCall>>(m, "BracedCall", node))->def(py::init<std::shared_ptr<const Node>,std::vector<std::shared_ptr<const Node>>,py::tuple>());
        ceto::mado(py::class_<Template,std::shared_ptr<Template>>(m, "Template", node))->def(py::init<std::shared_ptr<const Node>,std::vector<std::shared_ptr<const Node>>,py::tuple>());
        ceto::mado(py::class_<Identifier,std::shared_ptr<Identifier>>(m, "Identifier", node))->def(py::init<const std::string &,py::tuple>());
        ceto::mado(py::class_<StringLiteral,std::shared_ptr<StringLiteral>>(m, "StringLiteral", node))->def(py::init<const std::string &,std::shared_ptr<const Identifier>,std::shared_ptr<const Identifier>,py::tuple>());
        ceto::mado(py::class_<IntegerLiteral,std::shared_ptr<IntegerLiteral>>(m, "IntegerLiteral", node))->def(py::init<const std::string &,std::shared_ptr<const Identifier>,py::tuple>());
        ceto::mado(py::class_<FloatLiteral,std::shared_ptr<FloatLiteral>>(m, "FloatLiteral", node))->def(py::init<const std::string &,std::shared_ptr<const Identifier>,py::tuple>());
        auto list_like { py::class_<ListLike_,std::shared_ptr<ListLike_>>(m, "ListLike_", node) } ;
        ceto::mado(py::class_<ListLiteral,std::shared_ptr<ListLiteral>>(m, "ListLiteral", list_like))->def(py::init<std::vector<std::shared_ptr<const Node>>,py::tuple>());
        ceto::mado(py::class_<TupleLiteral,std::shared_ptr<TupleLiteral>>(m, "TupleLiteral", list_like))->def(py::init<std::vector<std::shared_ptr<const Node>>,py::tuple>());
        ceto::mado(py::class_<BracedLiteral,std::shared_ptr<BracedLiteral>>(m, "BracedLiteral", list_like))->def(py::init<std::vector<std::shared_ptr<const Node>>,py::tuple>());
        auto block { py::class_<Block,std::shared_ptr<Block>>(m, "Block", list_like) } ;
        ceto::mado(block)->def(py::init<std::vector<std::shared_ptr<const Node>>,py::tuple>());
        ceto::mado(py::class_<Module,std::shared_ptr<Module>>(m, "Module", block))->def(py::init<std::vector<std::shared_ptr<const Node>>,py::tuple>());
        ceto::mado(py::class_<RedundantParens,std::shared_ptr<RedundantParens>>(m, "RedundantParens", node))->def(py::init<std::vector<std::shared_ptr<const Node>>,py::tuple>());
        ceto::mado(m)->def("macro_trampoline", (&macro_trampoline), "macro trampoline");
        return;
        }(m);
};
