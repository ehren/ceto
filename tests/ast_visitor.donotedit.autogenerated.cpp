
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
            std::cout << std::string {"BaseVisitor visiting Node\n"};
        }

         virtual inline auto visit(const std::shared_ptr<const Identifier>&  ident) -> void {
            std::cout << std::string {"BaseVisitor visiting Identifier\n"};
        }

         virtual inline auto visit(const std::shared_ptr<const ListLiteral>&  list_literal) -> void {
            std::cout << std::string {"BaseVisitor visiting ListLiteral\n"};
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
            (this -> record) += std::string {"RecordingVisitor visiting Node\n"};
        }

         virtual inline auto visit(const std::shared_ptr<const Identifier>&  ident) -> void {
            (this -> record) += std::string {"RecordingVisitor visiting Identifier\n"};
        }

         virtual inline auto visit(const std::shared_ptr<const ListLiteral>&  list_literal) -> void {
            const auto self = ceto::shared_from(this);
            (this -> record) += std::string {"RecordingVisitor visiting ListLiteral\n"};
            for(const auto& arg : ceto::mado(list_literal)->args) {
                ceto::mado(arg)->accept(self);
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
        const std::vector<std::shared_ptr<const Node>> list_args = std::vector<std::shared_ptr<const Node>>{ident, ident, ident}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<std::shared_ptr<const Node>>{ident, ident, ident}), std::remove_cvref_t<decltype(list_args)>>);
        const auto list_literal = std::make_shared<const decltype(ListLiteral{list_args})>(list_args);
        ceto::mado(list_literal)->accept(simple_visitor);
        ceto::mado(list_literal)->accept(recording_visitor);
        std::cout << ceto::mado(recording_visitor)->record;
    }

