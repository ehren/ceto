
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
struct Node : ceto::shared_object {

    std::shared_ptr<const Node> func;

    std::vector<std::shared_ptr<const Node>> args;

    py::tuple source;

    py::object parent = py::none(); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(py::none()), std::remove_cvref_t<decltype(parent)>>);

    std::shared_ptr<const Node> declared_type = nullptr; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(nullptr), std::remove_cvref_t<decltype(declared_type)>>);

    py::object scope = py::none(); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(py::none()), std::remove_cvref_t<decltype(scope)>>);

         virtual inline auto repr() const -> std::string {
            const std::string classname = ceto::mad(typeid((*this)))->name(); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(ceto::mad(typeid((*this)))->name()), std::remove_cvref_t<decltype(classname)>>);
            auto args_str { std::string {"["} } ;
            for(const auto& a : (this -> args)) {
                args_str += (ceto::mad(a)->repr() + std::string {", "});
            }
            args_str += std::string {"]"};
            return (((((classname + std::string {"("}) + ceto::mad(this -> func)->repr()) + std::string {")("}) + args_str) + std::string {")"});
        }

         virtual inline auto name() const -> std::optional<std::string> {
            return nullptr;
        }

    explicit Node(const std::shared_ptr<const Node>&  func, const std::vector<std::shared_ptr<const Node>>&  args, const decltype(py::tuple{}) source = py::tuple{}) : func(func), args(args), source(source) {
    }

    Node() = delete;

};

struct UnOp : public Node {

};

struct LeftAssociativeUnOp : public Node {

};

struct BinOp : public Node {

        inline auto lhs() const -> auto {
            return ceto::maybe_bounds_check_access(this -> args,0);
        }

        inline auto rhs() const -> auto {
            return ceto::maybe_bounds_check_access(this -> args,1);
        }

        inline auto repr() const -> std::string {
            return ((ceto::mad(this -> lhs())->repr() + ceto::mad(this -> func)->repr()) + ceto::mad(this -> rhs())->repr());
        }

};

struct TypeOp : public BinOp {

};

struct SyntaxTypeOp : public TypeOp {

};

struct AttributeAccess : public BinOp {

        inline auto repr() const -> std::string {
            return ((ceto::mad(this -> lhs())->repr() + std::string {"."}) + ceto::mad(this -> rhs())->repr());
        }

};

struct ArrowOp : public BinOp {

};

struct ScopeResolution : public BinOp {

};

struct Assign : public BinOp {

};

struct Identifier : public decltype(Node(nullptr, std::vector<std::shared_ptr<const Node>>{}, std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>())) {

    std::string _name;

        inline auto repr() const -> std::string {
            return (this -> _name);
        }

        inline auto name() const -> std::optional<std::string> {
            return (this -> _name);
        }

    explicit Identifier(const std::string&  name, const decltype(py::tuple{}) source = py::tuple{}) : decltype(Node(nullptr, std::vector<std::shared_ptr<const Node>>{}, std::declval<std::remove_cvref_t<const decltype(py::tuple{})>>())) (nullptr, std::vector<std::shared_ptr<const Node>>{}, source), _name(name) {
    }

    Identifier() = delete;

};

    template <typename T1, typename T2>
auto join(const T1& v, const T2& to_string, const decltype(std::string {""})&  sep = std::string {""}) -> auto {
if (ceto::mad(v)->empty()) {
            return std::string {""};
        }
        return std::accumulate(ceto::mad(v)->cbegin() + 1, ceto::mad(v)->cend(), to_string(ceto::maybe_bounds_check_access(v,0)), [&to_string, &sep](const auto &a, const auto &el) {
                if constexpr (!std::is_void_v<decltype(((a + sep) + to_string(el)))>) { return ((a + sep) + to_string(el)); } else { static_cast<void>(((a + sep) + to_string(el))); };
                });
    }

struct Call : public Node {

        inline auto repr() const -> std::string {
            const auto csv = join(this -> args, [](const auto &a) {
                    if constexpr (!std::is_void_v<decltype(ceto::mad(a)->repr())>) { return ceto::mad(a)->repr(); } else { static_cast<void>(ceto::mad(a)->repr()); };
                    }, std::string {", "});
            return (((ceto::mad(this -> func)->repr() + std::string {"("}) + csv) + std::string {")"});
        }

};

    inline auto example_macro_body_workaround_no_fptr_syntax_yet(const std::map<std::string,std::shared_ptr<const Node>>  matches) -> std::shared_ptr<const Node> {
        return nullptr;
    }

    inline auto macro_trampoline(const uintptr_t  fptr, const std::map<std::string,std::shared_ptr<const Node>>  matches) -> auto {
        const auto f = reinterpret_cast<decltype(&example_macro_body_workaround_no_fptr_syntax_yet)>(fptr);
        return (*f)(matches);
    }


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
;
[]( auto &&  m) {
        py::bind_vector<std::vector<std::shared_ptr<const Node>>>(m, "VectorNode");
        py::bind_map<std::map<std::string,std::shared_ptr<const Node>>>(m, "MapStringNode");
        auto node { ceto::mad(ceto::mad(ceto::mad(ceto::mad(ceto::mad(ceto::mad(ceto::mad(ceto::mad(py::class_<std::type_identity_t<std::shared_ptr<Node>> :: element_type,std::shared_ptr<Node>>(m, "Node"))->def_readwrite("func", (&Node::func)))->def_readwrite("args", (&Node::args)))->def_readwrite("parent", (&Node::parent)))->def_readwrite("declared_type", (&Node::declared_type)))->def_readwrite("scope", (&Node::scope)))->def_readwrite("source", (&Node::source)))->def("__repr__", (&Node::repr)))->def("name", (&Node::name)) } ;
        ceto::mad(py::class_<std::type_identity_t<std::shared_ptr<Identifier>> :: element_type,std::shared_ptr<Identifier>>(m, "Identifier", node))->def(py::init<const std::string &,py::tuple>());
        ceto::mad(m)->def("macro_trampoline", (&macro_trampoline), "macro trampoline");
        return;
        }(m);
};
