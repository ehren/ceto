
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

class Node;

class Identifier;

class ListLiteral;

struct BaseVisitor : ceto::shared_object {

         virtual inline auto visit(const std::shared_ptr<const Node>&  node) -> void {
            std::cout << std::string {"visiting Node\n"};
        }

         virtual inline auto visit(const std::shared_ptr<const Identifier>&  ident) -> void {
            std::cout << std::string {"visiting Identifier\n"};
        }

         virtual inline auto visit(const std::shared_ptr<const ListLiteral>&  list_literal) -> void {
            std::cout << std::string {"visiting ListLiteral\n"};
        }

};

struct Node : ceto::shared_object {

         virtual inline auto accept(const std::shared_ptr<BaseVisitor>&  visitor) const -> void {
            const auto self = ceto::shared_from(this);
            ceto::mado(visitor)->visit(self);
        }

};

struct Identifier : public Node {

    std::string _name;

         virtual inline auto accept(const std::shared_ptr<BaseVisitor>&  visitor) const -> void {
            const auto self = ceto::shared_from(this);
            ceto::mado(visitor)->visit(self);
        }

    explicit Identifier(const std::string&  name) : _name(name) {
    }

    Identifier() = delete;

};

struct ListLiteral : public Node {

    std::vector<std::shared_ptr<const Node>> args;

         virtual inline auto accept(const std::shared_ptr<BaseVisitor>&  visitor) const -> void {
            const auto self = ceto::shared_from(this);
            ceto::mado(visitor)->visit(self);
        }

    explicit ListLiteral(const std::vector<std::shared_ptr<const Node>>&  args) : args(args) {
    }

    ListLiteral() = delete;

};

struct RecordingVisitor : public BaseVisitor {

using BaseVisitor::BaseVisitor;

    std::remove_cvref_t<decltype(std::string {""})> record = std::string {""};

         virtual inline auto visit(const std::shared_ptr<const Node>&  node) -> void {
            (this -> record) += std::string {"recording Node visit\n"};
        }

         virtual inline auto visit(const std::shared_ptr<const Identifier>&  ident) -> void {
            (this -> record) += std::string {"recording Ident visit\n"};
        }

         virtual inline auto visit(const std::shared_ptr<const ListLiteral>&  list_literal) -> void {
            std::cout << std::string {"visiting ListLiteral\n"};
            for(const auto& arg : ceto::mado(list_literal)->args) {
                this -> visit(arg);
            }
        }

};

    auto main() -> int {
        const auto node = std::make_shared<const decltype(Node())>();
        const auto ident = std::make_shared<const decltype(Identifier{std::string {"a"}})>(std::string {"a"});
        auto simple_visitor { std::make_shared<decltype(BaseVisitor())>() } ;
        ceto::mado(ident)->accept(simple_visitor);
        ceto::mado(node)->accept(simple_visitor);
        auto recording_visitor { std::make_shared<decltype(RecordingVisitor())>() } ;
        ceto::mado(ident)->accept(recording_visitor);
        ceto::mado(node)->accept(recording_visitor);
        const auto list_literal = std::make_shared<const decltype(ListLiteral{std::vector {{ident, ident, ident}}})>(std::vector {{ident, ident, ident}});
        ceto::mado(simple_visitor)->accept(list_literal);
        ceto::mado(recording_visitor)->accept(list_literal);
        std::cout << ceto::mado(recording_visitor)->record;
    }

