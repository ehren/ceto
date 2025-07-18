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


#include "ceto.h"

#include "ceto_private_listcomp.donotedit.autogenerated.h"
;
#include "ceto_private_boundscheck.donotedit.autogenerated.h"
;
#include "ceto_private_convenience.donotedit.autogenerated.h"
;
#include "ceto_private_append_to_pushback.donotedit.autogenerated.h"
;
#include <map>
;
#include <typeinfo>
;
#include <variant>
;

;
#include "visitor.donotedit.autogenerated.h"
;

;
#include "utility.donotedit.autogenerated.h"
;

;
#include "range_utility.donotedit.autogenerated.h"
;
// unsafe;
struct Source : public ceto::shared_object, public std::enable_shared_from_this<Source> {

    decltype(std::string {""}) source = std::string {""};

};

struct SourceLoc : public ceto::object {

    ceto::propagate_const<std::shared_ptr<const Source>> source;

    int loc;

    decltype(std::string {""}) header_file_cth = std::string {""};

    decltype(std::string {""}) header_file_h = std::string {""};

    explicit SourceLoc(const ceto::propagate_const<std::shared_ptr<const Source>>& source = nullptr, const int loc = 0) : source(source), loc(loc) {
    }

};

struct Scope;

struct Node : public ceto::shared_object, public std::enable_shared_from_this<Node> {

    ceto::propagate_const<std::shared_ptr<const Node>> func;

    std::vector<ceto::propagate_const<std::shared_ptr<const Node>>> args;

    SourceLoc source;

    ceto::propagate_const<std::shared_ptr<const Node>> declared_type = nullptr; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(nullptr), std::remove_cvref_t<decltype(declared_type)>>);

    ceto::propagate_const<std::shared_ptr<const Scope>> scope = nullptr; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(nullptr), std::remove_cvref_t<decltype(scope)>>);

    std::weak_ptr<const Node> _parent = {};

         virtual inline auto classname() const -> std::string {
            return ceto::util::typeid_name((*this));
        }

         virtual inline auto repr() const -> std::string {
            const auto classname = this -> classname();
            const auto csv = ceto::util::join(this -> args, [](const auto &a) {
                    return (*ceto::mad(a)).repr();
                    }, ", ");
            return (((((classname + "(") + [&]() {if (this -> func) {
                return (*ceto::mad(this -> func)).repr();
            } else {
                return std::string {""};
            }}()
) + ")([") + csv) + "])");
        }

         virtual inline auto name() const -> std::optional<std::string> {
            return std::nullopt;
        }

         virtual inline auto accept( Visitor &  visitor) const -> void {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto cloned_args() const -> std::vector<ceto::propagate_const<std::shared_ptr<const Node>>> {
            std::vector<ceto::propagate_const<std::shared_ptr<const Node>>> new_args = std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>{}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>{}), std::remove_cvref_t<decltype(new_args)>>);
            (*ceto::mad(new_args)).reserve((*ceto::mad(this -> args)).size());
            
                auto&& ceto__private__intermediate1 = this -> args;

                static_assert(requires { std::begin(ceto__private__intermediate1) + 2; }, "not a contiguous container");
                size_t ceto__private__size3 = std::size(ceto__private__intermediate1);
                for (size_t ceto__private__idx2 = 0; ; ceto__private__idx2++) {
                    if (std::size(ceto__private__intermediate1) != ceto__private__size3) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx2 >= ceto__private__size3) {
                        break;
                    }
                    const auto a = ceto__private__intermediate1[ceto__private__idx2];
                                    (new_args).push_back((*ceto::mad(a)).clone());

                }
                return new_args;
        }

         virtual inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> {
            ceto::propagate_const<std::shared_ptr<Node>> none = nullptr; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(nullptr), std::remove_cvref_t<decltype(none)>>);
            auto c { ceto::make_shared_propagate_const<Node>([&]() {if (this -> func) {
                return (*ceto::mad(this -> func)).clone();
            } else {
                return none;
            }}()
, this -> cloned_args(), this -> source) } ;
            return c;
        }

         virtual inline auto equals(const ceto::propagate_const<std::shared_ptr<const Node>>&  other) const -> bool {
            if (other == nullptr) {
                return false;
            }
            if (this -> classname() != (*ceto::mad(other)).classname()) {
                return false;
            }
            if ((this -> func) && !(*ceto::mad(this -> func)).equals((*ceto::mad(other)).func)) {
                return false;
            } else if ((!(this -> func) && (*ceto::mad(other)).func)) {
                return false;
            }
            if ((*ceto::mad(this -> args)).size() != (*ceto::mad((*ceto::mad(other)).args)).size()) {
                return false;
            }
            
                auto&& ceto__private__intermediate4 = this -> args;
            auto&& ceto__private__intermediate6 = (*ceto::mad(ceto__private__intermediate4)).size();
            auto&& ceto__private__intermediate7 = ceto::util::range(ceto__private__intermediate6);

                static_assert(requires { std::begin(ceto__private__intermediate7) + 2; }, "not a contiguous container");
                size_t ceto__private__size9 = std::size(ceto__private__intermediate7);
                for (size_t ceto__private__idx8 = 0; ; ceto__private__idx8++) {
                    if (std::size(ceto__private__intermediate7) != ceto__private__size9) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx8 >= ceto__private__size9) {
                        break;
                    }
                    const auto i = ceto__private__intermediate7[ceto__private__idx8];
                                    if (!(*ceto::mad((*ceto::mad(this -> args)).at(i))).equals((*ceto::mad((*ceto::mad(other)).args)).at(i))) {
                                return false;
                            }

                }
                return true;
        }

        inline auto replace(const ceto::propagate_const<std::shared_ptr<const Node>>&  pattern, const ceto::propagate_const<std::shared_ptr<const Node>>&  replacement) -> ceto::propagate_const<std::shared_ptr<Node>> {
            const auto self = ceto::shared_from(this);
            if (this -> equals(pattern)) {
                return (*ceto::mad(replacement)).clone();
            }
            
                auto&& ceto__private__intermediate10 = this -> args;
            auto&& ceto__private__intermediate12 = (*ceto::mad(ceto__private__intermediate10)).size();
            auto&& ceto__private__intermediate13 = ceto::util::range(ceto__private__intermediate12);

                static_assert(requires { std::begin(ceto__private__intermediate13) + 2; }, "not a contiguous container");
                size_t ceto__private__size15 = std::size(ceto__private__intermediate13);
                for (size_t ceto__private__idx14 = 0; ; ceto__private__idx14++) {
                    if (std::size(ceto__private__intermediate13) != ceto__private__size15) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx14 >= ceto__private__size15) {
                        break;
                    }
                    const auto i = ceto__private__intermediate13[ceto__private__idx14];
                                    (*ceto::mad(this -> args)).at(i) = (*ceto::mad((*ceto::mad(this -> args)).at(i))).replace(pattern, replacement);

                }
                (this -> func) = [&]() {if (this -> func) {
                return (*ceto::mad(this -> func)).replace(pattern, replacement);
            } else {
                const ceto::propagate_const<std::shared_ptr<const Node>> none = nullptr; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(nullptr), std::remove_cvref_t<decltype(none)>>);
                return none;
            }}()
;
            return self;
        }

        inline auto replace(const ceto::propagate_const<std::shared_ptr<const Node>>&  pattern, const ceto::propagate_const<std::shared_ptr<const Node>>&  replacement) const -> ceto::propagate_const<std::shared_ptr<const Node>> {
            auto c { this -> clone() } ;
            c = (*ceto::mad(c)).replace(pattern, replacement);
            return c;
        }

        inline auto parent() const -> ceto::propagate_const<std::shared_ptr<const Node>> {
            return (*ceto::mad(this -> _parent)).lock();
        }

        inline auto set_parent(const ceto::propagate_const<std::shared_ptr<const Node>>&  p) -> void {
            (this -> _parent) = ceto::get_underlying(p);
        }

         virtual ~Node() = default;

    explicit Node(const ceto::propagate_const<std::shared_ptr<const Node>>&  func, const std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>&  args, const decltype(SourceLoc())& source = SourceLoc()) : func(func), args(args), source(source) {
    }

    Node() = delete;

};

struct UnOp : public Node {

    std::string op;

        inline auto repr() const -> std::string override {
            return ((((std::string {"("} + (this -> op)) + " ") + (*ceto::mad((*ceto::mad(this -> args)).at(0))).repr()) + ")");
        }

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<UnOp>(this -> op, this -> cloned_args(), source) } ;
            return c;
        }

    explicit UnOp(const std::string&  op, const std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>&  args, const decltype(SourceLoc())& source = SourceLoc()) : Node (nullptr, args, source), op(op) {
    }

    UnOp() = delete;

};

struct LeftAssociativeUnOp : public Node {

    std::string op;

        inline auto repr() const -> std::string override {
            return (((("(" + (*ceto::mad((*ceto::mad(this -> args)).at(0))).repr()) + " ") + (this -> op)) + ")");
        }

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<LeftAssociativeUnOp>(this -> op, this -> cloned_args(), source) } ;
            return c;
        }

    explicit LeftAssociativeUnOp(const std::string&  op, const std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>&  args, const decltype(SourceLoc())& source = SourceLoc()) : Node (nullptr, args, source), op(op) {
    }

    LeftAssociativeUnOp() = delete;

};

struct BinOp : public Node {

    std::string op;

        inline auto lhs() const -> auto {
            return (*ceto::mad(this -> args)).at(0);
        }

        inline auto rhs() const -> auto {
            return (*ceto::mad(this -> args)).at(1);
        }

        inline auto repr() const -> std::string override {
            return (((((("(" + (*ceto::mad(this -> lhs())).repr()) + " ") + (this -> op)) + " ") + (*ceto::mad(this -> rhs())).repr()) + ")");
        }

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<BinOp>(this -> op, this -> cloned_args(), this -> source) } ;
            return c;
        }

        inline auto equals(const ceto::propagate_const<std::shared_ptr<const Node>>&  other_node) const -> bool override {
            const auto other = ceto::propagate_const<std::shared_ptr<const BinOp>>(std::dynamic_pointer_cast<const BinOp>(ceto::get_underlying(other_node)));
            if (!other) {
                return false;
            }
            if ((this -> op) != (*ceto::mad(other)).op) {
                return false;
            }
            return ((*ceto::mad(this -> lhs())).equals((*ceto::mad(other)).lhs()) && (*ceto::mad(this -> rhs())).equals((*ceto::mad(other)).rhs()));
        }

    explicit BinOp(const std::string&  op, const std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>&  args, const decltype(SourceLoc())& source = SourceLoc()) : Node (nullptr, args, source), op(op) {
    }

    BinOp() = delete;

};

struct TypeOp : public BinOp {

using BinOp::BinOp;

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<TypeOp>(this -> op, this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct SyntaxTypeOp : public TypeOp {

using TypeOp::TypeOp;

    ceto::propagate_const<std::shared_ptr<const Node>> synthetic_lambda_return_lambda = nullptr; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(nullptr), std::remove_cvref_t<decltype(synthetic_lambda_return_lambda)>>);

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<SyntaxTypeOp>(this -> op, this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct AttributeAccess : public BinOp {

using BinOp::BinOp;

        inline auto repr() const -> std::string override {
            return (((*ceto::mad(this -> lhs())).repr() + ".") + (*ceto::mad(this -> rhs())).repr());
        }

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<AttributeAccess>(this -> op, this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct ArrowOp : public BinOp {

using BinOp::BinOp;

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<ArrowOp>(this -> op, this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct ScopeResolution : public BinOp {

using BinOp::BinOp;

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<ScopeResolution>(this -> op, this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct Assign : public BinOp {

using BinOp::BinOp;

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<Assign>(this -> op, this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct NamedParameter : public Assign {

using Assign::Assign;

        inline auto repr() const -> std::string override {
            return ((std::string {"NamedParameter("} + ceto::util::join(this -> args, [](const auto &a) {
                    return (*ceto::mad(a)).repr();
                    }, ", ")) + ")");
        }

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<NamedParameter>(this -> op, this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct BitwiseOrOp : public BinOp {

using BinOp::BinOp;

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<BitwiseOrOp>(this -> op, this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct EqualsCompareOp : public BinOp {

using BinOp::BinOp;

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<EqualsCompareOp>(this -> op, this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct Identifier : public Node {

    std::string _name;

        inline auto repr() const -> std::string override {
            return (this -> _name);
        }

        inline auto name() const -> std::optional<std::string> override {
            return (this -> _name);
        }

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto equals(const ceto::propagate_const<std::shared_ptr<const Node>>&  other_node) const -> bool override {
            const auto other = ceto::propagate_const<std::shared_ptr<const Identifier>>(std::dynamic_pointer_cast<const Identifier>(ceto::get_underlying(other_node)));
            if (!other) {
                return false;
            }
            return ((this -> _name) == (*ceto::mad(other))._name);
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { std::make_shared<Identifier>((*this)) } ;
            return c;
        }

    explicit Identifier(const std::string&  name, const decltype(SourceLoc())& source = SourceLoc()) : Node (nullptr, std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>{}, source), _name(name) {
    }

    Identifier() = delete;

};

struct Call : public Node {

using Node::Node;

    decltype(false) is_one_liner_if = false;

        inline auto repr() const -> std::string override {
            const auto csv = ceto::util::join(this -> args, [](const auto &a) {
                    return (*ceto::mad(a)).repr();
                    }, ", ");
            return ((((*ceto::mad(this -> func)).repr() + "(") + csv) + ")");
        }

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<Call>((*ceto::mad(this -> func)).clone(), this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct ArrayAccess : public Node {

using Node::Node;

        inline auto repr() const -> std::string override {
            const auto csv = ceto::util::join(this -> args, [](const auto &a) {
                    return (*ceto::mad(a)).repr();
                    }, ", ");
            return ((((*ceto::mad(this -> func)).repr() + "[") + csv) + "]");
        }

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<ArrayAccess>((*ceto::mad(this -> func)).clone(), this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct BracedCall : public Node {

using Node::Node;

        inline auto repr() const -> std::string override {
            const auto csv = ceto::util::join(this -> args, [](const auto &a) {
                    return (*ceto::mad(a)).repr();
                    }, ", ");
            return ((((*ceto::mad(this -> func)).repr() + "{") + csv) + "}");
        }

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<BracedCall>((*ceto::mad(this -> func)).clone(), this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct Template : public Node {

using Node::Node;

        inline auto repr() const -> std::string override {
            const auto csv = ceto::util::join(this -> args, [](const auto &a) {
                    return (*ceto::mad(a)).repr();
                    }, ", ");
            return ((((*ceto::mad(this -> func)).repr() + "<") + csv) + ">");
        }

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<Template>((*ceto::mad(this -> func)).clone(), this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct StringLiteral : public Node {

    std::string str;

    ceto::propagate_const<std::shared_ptr<const Identifier>> prefix;

    ceto::propagate_const<std::shared_ptr<const Identifier>> suffix;

        inline auto escaped() const -> auto {
            auto s { ceto::util::string_replace(this -> str, "\\", "\\\\") } ;
            s = ceto::util::string_replace(s, "\n", "\\n");
            s = ceto::util::string_replace(s, "\"", "\\\"");
            s = ((std::string {"\""} + s) + "\"");
            return s;
        }

        inline auto repr() const -> std::string override {
            return (([&]() {if (this -> prefix) {
                return (*ceto::mad_smartptr((*ceto::mad(this -> prefix)).name())).value();
            } else {
                return std::string {""};
            }}()
 + this -> escaped()) + [&]() {if (this -> suffix) {
                return (*ceto::mad_smartptr((*ceto::mad(this -> suffix)).name())).value();
            } else {
                return std::string {""};
            }}()
);
        }

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto equals(const ceto::propagate_const<std::shared_ptr<const Node>>&  other_node) const -> bool override {
            const auto other = ceto::propagate_const<std::shared_ptr<const StringLiteral>>(std::dynamic_pointer_cast<const StringLiteral>(ceto::get_underlying(other_node)));
            if (!other) {
                return false;
            }
            if ((this -> str) != (*ceto::mad(other)).str) {
                return false;
            }
            if ((this -> prefix) && !(*ceto::mad(this -> prefix)).equals((*ceto::mad(other)).prefix)) {
                return false;
            } else if ((!(this -> prefix) && (*ceto::mad(other)).prefix)) {
                return false;
            }
            if ((this -> suffix) && !(*ceto::mad(this -> suffix)).equals((*ceto::mad(other)).suffix)) {
                return false;
            } else if ((!(this -> suffix) && (*ceto::mad(other)).suffix)) {
                return false;
            }
            return true;
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<StringLiteral>(this -> str, [&]() {if (this -> prefix) {
                return ceto::propagate_const<std::shared_ptr<const Identifier>>(std::dynamic_pointer_cast<const Identifier>(ceto::get_underlying((*ceto::mad(this -> prefix)).clone())));
            } else {
                return (this -> prefix);
            }}()
, [&]() {if (this -> suffix) {
                return ceto::propagate_const<std::shared_ptr<const Identifier>>(std::dynamic_pointer_cast<const Identifier>(ceto::get_underlying((*ceto::mad(this -> suffix)).clone())));
            } else {
                return (this -> suffix);
            }}()
, this -> source) } ;
            return c;
        }

    explicit StringLiteral(const std::string&  str, const ceto::propagate_const<std::shared_ptr<const Identifier>>& prefix = nullptr, const ceto::propagate_const<std::shared_ptr<const Identifier>>& suffix = nullptr, const decltype(SourceLoc())& source = SourceLoc()) : Node (nullptr, std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>{}, source), str(str), prefix(prefix), suffix(suffix) {
    }

    StringLiteral() = delete;

};

struct IntegerLiteral : public Node {

    std::string integer_string;

    ceto::propagate_const<std::shared_ptr<const Identifier>> suffix;

        inline auto repr() const -> std::string override {
            return ((this -> integer_string) + [&]() {if (this -> suffix) {
                return (*ceto::mad_smartptr((*ceto::mad(this -> suffix)).name())).value();
            } else {
                return std::string {""};
            }}()
);
        }

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<IntegerLiteral>(this -> integer_string, [&]() {if (this -> suffix) {
                return ceto::propagate_const<std::shared_ptr<const Identifier>>(std::dynamic_pointer_cast<const Identifier>(ceto::get_underlying((*ceto::mad(this -> suffix)).clone())));
            } else {
                return (this -> suffix);
            }}()
, this -> source) } ;
            return c;
        }

        inline auto equals(const ceto::propagate_const<std::shared_ptr<const Node>>&  other_node) const -> bool override {
            const auto other = ceto::propagate_const<std::shared_ptr<const IntegerLiteral>>(std::dynamic_pointer_cast<const IntegerLiteral>(ceto::get_underlying(other_node)));
            if (!other) {
                return false;
            }
            if ((this -> integer_string) != (*ceto::mad(other)).integer_string) {
                return false;
            }
            if ((this -> suffix) && !(*ceto::mad(this -> suffix)).equals((*ceto::mad(other)).suffix)) {
                return false;
            } else if ((!(this -> suffix) && (*ceto::mad(other)).suffix)) {
                return false;
            }
            return true;
        }

    explicit IntegerLiteral(const std::string&  integer_string, const ceto::propagate_const<std::shared_ptr<const Identifier>>& suffix = nullptr, const decltype(SourceLoc())& source = SourceLoc()) : Node (nullptr, {}, source), integer_string(integer_string), suffix(suffix) {
    }

    IntegerLiteral() = delete;

};

struct FloatLiteral : public Node {

    std::string float_string;

    ceto::propagate_const<std::shared_ptr<const Identifier>> suffix;

        inline auto repr() const -> std::string override {
            return ((this -> float_string) + [&]() {if (this -> suffix) {
                return (*ceto::mad_smartptr((*ceto::mad(this -> suffix)).name())).value();
            } else {
                return std::string {""};
            }}()
);
        }

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto equals(const ceto::propagate_const<std::shared_ptr<const Node>>&  other_node) const -> bool override {
            const auto other = ceto::propagate_const<std::shared_ptr<const FloatLiteral>>(std::dynamic_pointer_cast<const FloatLiteral>(ceto::get_underlying(other_node)));
            if (!other) {
                return false;
            }
            if ((this -> float_string) != (*ceto::mad(other)).float_string) {
                return false;
            }
            if ((this -> suffix) && !(*ceto::mad(this -> suffix)).equals((*ceto::mad(other)).suffix)) {
                return false;
            } else if ((!(this -> suffix) && (*ceto::mad(other)).suffix)) {
                return false;
            }
            return true;
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<FloatLiteral>(this -> float_string, [&]() {if (this -> suffix) {
                return ceto::propagate_const<std::shared_ptr<const Identifier>>(std::dynamic_pointer_cast<const Identifier>(ceto::get_underlying((*ceto::mad(this -> suffix)).clone())));
            } else {
                return (this -> suffix);
            }}()
, this -> source) } ;
            return c;
        }

    explicit FloatLiteral(const std::string&  float_string, const ceto::propagate_const<std::shared_ptr<const Identifier>>&  suffix, const decltype(SourceLoc())& source = SourceLoc()) : Node (nullptr, {}, source), float_string(float_string), suffix(suffix) {
    }

    FloatLiteral() = delete;

};

struct ListLike_ : public Node {

        inline auto repr() const -> std::string override {
            const auto classname = this -> classname();
            return (((classname + "(") + ceto::util::join(this -> args, [](const auto &a) {
                    return (*ceto::mad(a)).repr();
                    }, ", ")) + ")");
        }

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<ListLike_>(this -> cloned_args(), this -> source) } ;
            return c;
        }

    explicit ListLike_(const std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>&  args, const decltype(SourceLoc())& source = SourceLoc()) : Node (nullptr, args, source) {
    }

    ListLike_() = delete;

};

struct ListLiteral : public ListLike_ {

using ListLike_::ListLike_;

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<ListLiteral>(this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct TupleLiteral : public ListLike_ {

using ListLike_::ListLike_;

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<TupleLiteral>(this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct BracedLiteral : public ListLike_ {

using ListLike_::ListLike_;

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<BracedLiteral>(this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct Block : public ListLike_ {

using ListLike_::ListLike_;

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<Block>(this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct Module : public Block {

using Block::Block;

    decltype(false) has_main_function = false;

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<Module>(this -> cloned_args(), this -> source) } ;
            return c;
        }

};

struct RedundantParens : public Node {

        inline auto repr() const -> std::string override {
            const auto classname = this -> classname();
            return (((classname + "(") + ceto::util::join(this -> args, [](const auto &a) {
                    return (*ceto::mad(a)).repr();
                    }, ", ")) + ")");
        }

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<RedundantParens>(this -> cloned_args(), this -> source) } ;
            return c;
        }

    explicit RedundantParens(const std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>&  args, const decltype(SourceLoc())& source = SourceLoc()) : Node (nullptr, args, source) {
    }

    RedundantParens() = delete;

};

struct InfixWrapper_ : public Node {

        inline auto repr() const -> std::string override {
            const auto classname = this -> classname();
            return (((classname + "(") + ceto::util::join(this -> args, [](const auto &a) {
                    return (*ceto::mad(a)).repr();
                    }, ", ")) + ")");
        }

        inline auto accept( Visitor &  visitor) const -> void override {
            (*ceto::mad(visitor)).visit((*this));
        }

        inline auto clone() const -> ceto::propagate_const<std::shared_ptr<Node>> override {
            auto c { ceto::make_shared_propagate_const<InfixWrapper_>(this -> cloned_args(), this -> source) } ;
            return c;
        }

    explicit InfixWrapper_(const std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>&  args, const decltype(SourceLoc())& source = SourceLoc()) : Node (nullptr, args, source) {
    }

    InfixWrapper_() = delete;

};

    inline auto gensym() -> auto {
        static unsigned long long counter { 0 } ; static_assert(std::is_convertible_v<decltype(0), decltype(counter)>);
        const auto s = ceto::make_shared_propagate_const<const Identifier>("ceto__private__ident__" + std::to_string(counter));
        counter += 1;
        return s;
    }

namespace ceto::macros {
    struct Skip : public ceto::object {

        };


};
