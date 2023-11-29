
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


struct Node;

struct Identifier;

struct BinOp;

struct Add;

struct Visitor : public ceto::shared_object, public std::enable_shared_from_this<Visitor> {

         virtual auto visit(const std::shared_ptr<const Node>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const Identifier>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const BinOp>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const Add>&  node) -> void = 0;

};

struct Node : public ceto::shared_object, public std::enable_shared_from_this<Node> {

    int loc;

         virtual inline auto accept(const std::shared_ptr<Visitor>&  visitor) const -> void {
            const auto self = ceto::shared_from(this);
            ceto::mado(visitor)->visit(self);
        }

    explicit Node(int loc) : loc(loc) {}

    Node() = delete;

};

struct Identifier : public Node {

    std::string name;

         virtual inline auto accept(const std::shared_ptr<Visitor>&  visitor) const -> void {
            const auto self = ceto::shared_from(this);
            ceto::mado(visitor)->visit(self);
        }

    explicit Identifier(const std::string&  name, const decltype(0) loc = 0) : Node (std::move(loc)), name(name) {
    }

    Identifier() = delete;

};

struct BinOp : public Node {

    std::vector<std::shared_ptr<const Node>> args;

         virtual inline auto accept(const std::shared_ptr<Visitor>&  visitor) const -> void {
            const auto self = ceto::shared_from(this);
            ceto::mado(visitor)->visit(self);
        }

    explicit BinOp(const std::vector<std::shared_ptr<const Node>>&  args, const decltype(0) loc = 0) : Node (std::move(loc)), args(args) {
    }

    BinOp() = delete;

};

struct Add : public BinOp {

using BinOp::BinOp;

         virtual inline auto accept(const std::shared_ptr<Visitor>&  visitor) const -> void {
            const auto self = ceto::shared_from(this);
            ceto::mado(visitor)->visit(self);
        }

};

struct SimpleVisitor : public Visitor {

using Visitor::Visitor;

    decltype(std::string {""}) record = std::string {""};

         virtual inline auto visit(const std::shared_ptr<const Node>&  node) -> void {
            (this -> record) += "visiting Node\n";
        }

         virtual inline auto visit(const std::shared_ptr<const Identifier>&  ident) -> void {
            (this -> record) += (("visiting Identifier " + ceto::mado(ident)->name) + "\n");
        }

         virtual inline auto visit(const std::shared_ptr<const BinOp>&  node) -> void {
            const auto self = ceto::shared_from(this);
            (this -> record) += "visiting BinOp\n";
            for(const auto& arg : ceto::mado(node)->args) {
                ceto::mado(arg)->accept(self);
            }
        }

         virtual inline auto visit(const std::shared_ptr<const Add>&  node) -> void {
            const auto self = ceto::shared_from(this);
            (this -> record) += "visiting Add\n";
            for(const auto& arg : ceto::mado(node)->args) {
                ceto::mado(arg)->accept(self);
            }
        }

};

    auto main() -> int {
        const auto node = std::make_shared<const decltype(Node{0})>(0);
        const auto ident = std::make_shared<const decltype(Identifier{"a", 5})>("a", 5);
        const std::vector<std::shared_ptr<const Node>> args = std::vector<std::shared_ptr<const Node>>{ident, node, ident}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<std::shared_ptr<const Node>>{ident, node, ident}), std::remove_cvref_t<decltype(args)>>);
        const std::shared_ptr<const Add> add = std::make_shared<const decltype(Add{args})>(args); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::make_shared<const decltype(Add{args})>(args)), std::remove_cvref_t<decltype(add)>>);
        auto simple_visitor { std::make_shared<decltype(SimpleVisitor())>() } ;
        ceto::mado(ident)->accept(simple_visitor);
        ceto::mado(add)->accept(simple_visitor);
        std::cout << ceto::mado(simple_visitor)->record;
    }

