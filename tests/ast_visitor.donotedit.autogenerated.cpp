
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

struct ListLiteral;

struct BaseVisitor : public ceto::shared_object, public std::enable_shared_from_this<BaseVisitor> {

         virtual auto visit(const std::shared_ptr<const Node>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const Identifier>&  ident) -> void = 0;

         virtual auto visit(const std::shared_ptr<const ListLiteral>&  list_literal) -> void = 0;

};

struct Node : public ceto::shared_object, public std::enable_shared_from_this<Node> {

         virtual inline auto accept(const std::shared_ptr<BaseVisitor>&  visitor) const -> void {
            const auto self = ceto::shared_from(this);
            (*ceto::mad(visitor)).visit(self);
        }

};

struct Identifier : public Node {

using Node::Node;

    std::string name;

         virtual inline auto accept(const std::shared_ptr<BaseVisitor>&  visitor) const -> void {
            const auto self = ceto::shared_from(this);
            (*ceto::mad(visitor)).visit(self);
        }

    explicit Identifier(std::string name) : name(std::move(name)) {}

    Identifier() = delete;

};

struct ListLiteral : public Node {

using Node::Node;

    std::vector<std::shared_ptr<const Node>> args;

         virtual inline auto accept(const std::shared_ptr<BaseVisitor>&  visitor) const -> void {
            const auto self = ceto::shared_from(this);
            (*ceto::mad(visitor)).visit(self);
        }

    explicit ListLiteral(std::vector<std::shared_ptr<const Node>> args) : args(std::move(args)) {}

    ListLiteral() = delete;

};

struct SimpleVisitor : public BaseVisitor {

using BaseVisitor::BaseVisitor;

         virtual inline auto visit(const std::shared_ptr<const Node>&  node) -> void {
            std::cout << "SimpleVisitor visiting Node\n";
        }

         virtual inline auto visit(const std::shared_ptr<const Identifier>&  ident) -> void {
            std::cout << "SimpleVisitor visiting Identifier\n";
        }

         virtual inline auto visit(const std::shared_ptr<const ListLiteral>&  list_literal) -> void {
            std::cout << "SimpleVisitor visiting ListLiteral\n";
        }

};

struct RecordingVisitor : public BaseVisitor {

using BaseVisitor::BaseVisitor;

    decltype(std::string {""}) record = std::string {""};

         virtual inline auto visit(const std::shared_ptr<const Node>&  node) -> void {
            (this -> record) += "RecordingVisitor visiting Node\n";
        }

         virtual inline auto visit(const std::shared_ptr<const Identifier>&  ident) -> void {
            (this -> record) += "RecordingVisitor visiting Identifier\n";
        }

         virtual inline auto visit(const std::shared_ptr<const ListLiteral>&  list_literal) -> void {
            const auto self = ceto::shared_from(this);
            (this -> record) += "RecordingVisitor visiting ListLiteral\n";
            for(const auto& arg : (*ceto::mad(list_literal)).args) {
                (*ceto::mad(arg)).accept(self);
            }
        }

};

    auto main() -> int {
        const auto node = std::make_shared<const decltype(Node())>();
        const auto ident = std::make_shared<const decltype(Identifier{"a"})>("a");
        auto simple_visitor { std::make_shared<decltype(SimpleVisitor())>() } ;
        (*ceto::mad(ident)).accept(simple_visitor);
        (*ceto::mad(node)).accept(simple_visitor);
        auto recording_visitor { std::make_shared<decltype(RecordingVisitor())>() } ;
        (*ceto::mad(ident)).accept(recording_visitor);
        (*ceto::mad(node)).accept(recording_visitor);
        const std::vector<std::shared_ptr<const Node>> list_args = std::vector<std::shared_ptr<const Node>>{ident, ident, ident}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<std::shared_ptr<const Node>>{ident, ident, ident}), std::remove_cvref_t<decltype(list_args)>>);
        const auto list_literal = std::make_shared<const decltype(ListLiteral{list_args})>(list_args);
        (*ceto::mad(list_literal)).accept(simple_visitor);
        (*ceto::mad(list_literal)).accept(recording_visitor);
        std::cout << (*ceto::mad(recording_visitor)).record;
    }

