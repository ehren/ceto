#pragma once

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
;
#include <typeinfo>
;
#include "string_utils.donotedit.autogenerated.h"
;
#include "visitor.donotedit.autogenerated.h"
;
class Node;

    auto class_name(const Node *  node) -> std::string;

struct MacroScope : ceto::shared_object {

};

struct Node : ceto::shared_object {

    std::shared_ptr<const Node> func;

    std::vector<std::shared_ptr<const Node>> args;

    std::tuple<std::string, int> source;

    std::shared_ptr<const Node> declared_type = nullptr; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(nullptr), std::remove_cvref_t<decltype(declared_type)>>);

    std::shared_ptr<const MacroScope> macro_scope = nullptr; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(nullptr), std::remove_cvref_t<decltype(macro_scope)>>);

    std::weak_ptr<const Node> _parent = {};

    std::remove_cvref_t<decltype(false)> from_include = false;

         virtual inline auto repr() const -> std::string {
            const auto classname = class_name(this);
            const auto csv = join(this -> args, [](const auto &a) {
                    if constexpr (!std::is_void_v<decltype(ceto::mado(a)->repr())>) { return ceto::mado(a)->repr(); } else { static_cast<void>(ceto::mado(a)->repr()); };
                    }, std::string {", "});
            return (((((classname + std::string {"("}) + ceto::mado(this -> func)->repr()) + std::string {")(["}) + csv) + std::string {"])"});
        }

         virtual inline auto name() const -> std::optional<std::string> {
            return std::nullopt;
        }

         virtual inline auto parent() const -> std::shared_ptr<const Node> {
            return ceto::mado(this -> _parent)->lock();
        }

         virtual inline auto set_parent(const std::shared_ptr<const Node>&  p) -> void {
            (this -> _parent) = p;
        }

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

    explicit Node(const std::shared_ptr<const Node>&  func, const std::vector<std::shared_ptr<const Node>>&  args, const decltype(std::make_tuple(std::string {""}, 0)) source = std::make_tuple(std::string {""}, 0)) : func(func), args(args), source(source) {
    }

    Node() = delete;

};

struct UnOp : public std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> {

    std::string op;

        inline auto repr() const -> std::string {
            return ((((std::string {"("} + (this -> op)) + std::string {" "}) + ceto::mado(ceto::maybe_bounds_check_access(this -> args,0))->repr()) + std::string {")"});
        }

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

    explicit UnOp(const std::string&  op, const std::vector<std::shared_ptr<const Node>>&  args, const decltype(std::make_tuple(std::string {""}, 0)) source = std::make_tuple(std::string {""}, 0)) : std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> (nullptr, args, source), op(op) {
    }

    UnOp() = delete;

};

struct LeftAssociativeUnOp : public std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> {

    std::string op;

        inline auto repr() const -> std::string {
            return ((((std::string {"("} + ceto::mado(ceto::maybe_bounds_check_access(this -> args,0))->repr()) + std::string {" "}) + (this -> op)) + std::string {")"});
        }

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

    explicit LeftAssociativeUnOp(const std::string&  op, const std::vector<std::shared_ptr<const Node>>&  args, const decltype(std::make_tuple(std::string {""}, 0)) source = std::make_tuple(std::string {""}, 0)) : std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> (nullptr, args, source), op(op) {
    }

    LeftAssociativeUnOp() = delete;

};

struct BinOp : public std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> {

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

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

    explicit BinOp(const std::string&  op, const std::vector<std::shared_ptr<const Node>>&  args, const decltype(std::make_tuple(std::string {""}, 0)) source = std::make_tuple(std::string {""}, 0)) : std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> (nullptr, args, source), op(op) {
    }

    BinOp() = delete;

};

struct TypeOp : public BinOp {

using BinOp::BinOp;

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

};

struct SyntaxTypeOp : public TypeOp {

using TypeOp::TypeOp;

    std::shared_ptr<const Node> synthetic_lambda_return_lambda = nullptr; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(nullptr), std::remove_cvref_t<decltype(synthetic_lambda_return_lambda)>>);

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

};

struct AttributeAccess : public BinOp {

using BinOp::BinOp;

        inline auto repr() const -> std::string {
            return ((ceto::mado(this -> lhs())->repr() + std::string {"."}) + ceto::mado(this -> rhs())->repr());
        }

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

};

struct ArrowOp : public BinOp {

using BinOp::BinOp;

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

};

struct ScopeResolution : public BinOp {

using BinOp::BinOp;

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

};

struct Assign : public BinOp {

using BinOp::BinOp;

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

};

struct NamedParameter : public Assign {

using Assign::Assign;

        inline auto repr() const -> std::string {
            return ((std::string {"NamedParameter("} + join(this -> args, [](const auto &a) {
                    if constexpr (!std::is_void_v<decltype(ceto::mado(a)->repr())>) { return ceto::mado(a)->repr(); } else { static_cast<void>(ceto::mado(a)->repr()); };
                    }, std::string {", "})) + std::string {")"});
        }

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

};

struct Identifier : public std::type_identity_t<decltype(Node(nullptr, std::vector<std::shared_ptr<const Node>>{}, std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> {

    std::string _name;

        inline auto repr() const -> std::string {
            return (this -> _name);
        }

        inline auto name() const -> std::optional<std::string> {
            return (this -> _name);
        }

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

    explicit Identifier(const std::string&  name, const decltype(std::make_tuple(std::string {""}, 0)) source = std::make_tuple(std::string {""}, 0)) : std::type_identity_t<decltype(Node(nullptr, std::vector<std::shared_ptr<const Node>>{}, std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> (nullptr, std::vector<std::shared_ptr<const Node>>{}, source), _name(name) {
    }

    Identifier() = delete;

};

struct Call : public Node {

using Node::Node;

    std::remove_cvref_t<decltype(false)> is_one_liner_if = false;

        inline auto repr() const -> std::string {
            const auto csv = join(this -> args, [](const auto &a) {
                    if constexpr (!std::is_void_v<decltype(ceto::mado(a)->repr())>) { return ceto::mado(a)->repr(); } else { static_cast<void>(ceto::mado(a)->repr()); };
                    }, std::string {", "});
            return (((ceto::mado(this -> func)->repr() + std::string {"("}) + csv) + std::string {")"});
        }

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
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

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
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

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
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

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

};

    inline auto get_string_replace_function() -> auto {
        static std::function<std::string(std::string)> func = {};
        return func;
    }

    inline auto set_string_replace_function(const decltype(get_string_replace_function())  f) -> void {
        get_string_replace_function() = f;
    }

struct StringLiteral : public std::type_identity_t<decltype(Node(nullptr, std::vector<std::shared_ptr<const Node>>{}, std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> {

    std::string str;

    std::shared_ptr<const Identifier> prefix;

    std::shared_ptr<const Identifier> suffix;

        inline auto escaped() const -> auto {
            auto s { string_replace(this -> str, std::string {"\\"}, std::string {"\\\\"}) } ;
            s = string_replace(s, std::string {"\n"}, std::string {"\\n"});
            s = string_replace(s, std::string {"\""}, std::string {"\\\""});
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

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

    explicit StringLiteral(const std::string&  str, const std::shared_ptr<const Identifier>& prefix = nullptr, const std::shared_ptr<const Identifier>& suffix = nullptr, const decltype(std::make_tuple(std::string {""}, 0)) source = std::make_tuple(std::string {""}, 0)) : std::type_identity_t<decltype(Node(nullptr, std::vector<std::shared_ptr<const Node>>{}, std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> (nullptr, std::vector<std::shared_ptr<const Node>>{}, source), str(str), prefix(prefix), suffix(suffix) {
    }

    StringLiteral() = delete;

};

struct IntegerLiteral : public std::type_identity_t<decltype(Node(nullptr, {}, std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> {

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

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

    explicit IntegerLiteral(const std::string&  integer_string, const std::shared_ptr<const Identifier>& suffix = nullptr, const decltype(std::make_tuple(std::string {""}, 0)) source = std::make_tuple(std::string {""}, 0)) : std::type_identity_t<decltype(Node(nullptr, {}, std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> (nullptr, {}, source), integer_string(integer_string), suffix(suffix) {
    }

    IntegerLiteral() = delete;

};

struct FloatLiteral : public std::type_identity_t<decltype(Node(nullptr, {}, std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> {

    std::string float_string;

    std::shared_ptr<const Identifier> suffix;

        inline auto repr() const -> std::string {
            return ((this -> float_string) + [&]() {if (this -> suffix) {
                return ceto::mad(ceto::mado(this -> suffix)->name())->value();
            } else {
                return std::string {""};
            }}()
);
        }

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

    explicit FloatLiteral(const std::string&  float_string, const std::shared_ptr<const Identifier>&  suffix, const decltype(std::make_tuple(std::string {""}, 0)) source = std::make_tuple(std::string {""}, 0)) : std::type_identity_t<decltype(Node(nullptr, {}, std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> (nullptr, {}, source), float_string(float_string), suffix(suffix) {
    }

    FloatLiteral() = delete;

};

struct ListLike_ : public std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> {

        inline auto repr() const -> std::string {
            const auto classname = class_name(this);
            return (((classname + std::string {"("}) + join(this -> args, [](const auto &a) {
                    if constexpr (!std::is_void_v<decltype(ceto::mado(a)->repr())>) { return ceto::mado(a)->repr(); } else { static_cast<void>(ceto::mado(a)->repr()); };
                    }, std::string {", "})) + std::string {")"});
        }

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

    explicit ListLike_(const std::vector<std::shared_ptr<const Node>>&  args, const decltype(std::make_tuple(std::string {""}, 0)) source = std::make_tuple(std::string {""}, 0)) : std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> (nullptr, args, source) {
    }

    ListLike_() = delete;

};

struct ListLiteral : public ListLike_ {

using ListLike_::ListLike_;

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

};

struct TupleLiteral : public ListLike_ {

using ListLike_::ListLike_;

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

};

struct BracedLiteral : public ListLike_ {

using ListLike_::ListLike_;

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

};

struct Block : public ListLike_ {

using ListLike_::ListLike_;

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

};

struct Module : public Block {

using Block::Block;

    std::remove_cvref_t<decltype(false)> has_main_function = false;

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

};

struct RedundantParens : public std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> {

        inline auto repr() const -> std::string {
            const auto classname = class_name(this);
            return (((classname + std::string {"("}) + join(this -> args, [](const auto &a) {
                    if constexpr (!std::is_void_v<decltype(ceto::mado(a)->repr())>) { return ceto::mado(a)->repr(); } else { static_cast<void>(ceto::mado(a)->repr()); };
                    }, std::string {", "})) + std::string {")"});
        }

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

    explicit RedundantParens(const std::vector<std::shared_ptr<const Node>>&  args, const decltype(std::make_tuple(std::string {""}, 0)) source = std::make_tuple(std::string {""}, 0)) : std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> (nullptr, args, source) {
    }

    RedundantParens() = delete;

};

struct InfixWrapper_ : public std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> {

        inline auto repr() const -> std::string {
            const auto classname = class_name(this);
            return (((classname + std::string {"("}) + join(this -> args, [](const auto &a) {
                    if constexpr (!std::is_void_v<decltype(ceto::mado(a)->repr())>) { return ceto::mado(a)->repr(); } else { static_cast<void>(ceto::mado(a)->repr()); };
                    }, std::string {", "})) + std::string {")"});
        }

         virtual inline auto accept( Visitor &  visitor) const -> void {
            ceto::mado(visitor)->visit((*this));
        }

    explicit InfixWrapper_(const std::vector<std::shared_ptr<const Node>>&  args, const decltype(std::make_tuple(std::string {""}, 0)) source = std::make_tuple(std::string {""}, 0)) : std::type_identity_t<decltype(Node(nullptr, std::declval<std::remove_cvref_t<const std::vector<std::shared_ptr<const Node>>&>>(), std::declval<std::remove_cvref_t<const decltype(std::make_tuple(std::string {""}, 0))>>()))> (nullptr, args, source) {
    }

    InfixWrapper_() = delete;

};

    inline auto macro_trampoline(const uintptr_t  fptr, const std::map<std::string,std::shared_ptr<const Node>>  matches) -> auto {
        const auto f = reinterpret_cast<decltype(+[](const std::map<std::string,std::shared_ptr<const Node>>  matches) -> std::shared_ptr<const Node> {
                if constexpr (!std::is_void_v<decltype(nullptr)>&& !std::is_void_v<std::shared_ptr<const Node>>) { return nullptr; } else { static_cast<void>(nullptr); };
                })>(fptr);
        return (*f)(matches);
    }

