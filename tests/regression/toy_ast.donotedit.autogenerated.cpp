
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

struct Node : ceto::shared_object {

    std::shared_ptr<const Node> func;

    std::vector<std::shared_ptr<const Node>> args;

         virtual inline auto repr() const -> std::string {
            auto r { ((((std::string {"generic node with func "} + [&]() {if (this -> func) {
                return ceto::mado(this -> func)->repr();
            } else {
                return std::string {"none"};
            }}()
) + std::string {" ("}) + std::to_string(ceto::mado(this -> args)->size())) + std::string {" args.)\n"}) } ;
            for(const auto& a : (this -> args)) {
                r = ((r + std::string {"arg: "}) + ceto::mado(a)->repr());
            }
            return r;
        }

    explicit Node(std::shared_ptr<const Node> func, std::vector<std::shared_ptr<const Node>> args) : func(std::move(func)), args(std::move(args)) {}

    Node() = delete;

};

struct Identifier : public std::type_identity_t<decltype(Node(nullptr, std::vector<std::shared_ptr<const Node>>{}))> {

    std::string name;

        inline auto repr() const -> std::string {
            return ((std::string {"identifier node with name: "} + (this -> name)) + std::string {"\n"});
        }

    explicit Identifier(const std::string&  name) : std::type_identity_t<decltype(Node(nullptr, std::vector<std::shared_ptr<const Node>>{}))> (nullptr, std::vector<std::shared_ptr<const Node>>{}), name(name) {
    }

    Identifier() = delete;

};

    auto main() -> int {
        const auto id = std::make_shared<const decltype(Identifier{std::string {"a"}})>(std::string {"a"});
        std::cout << ceto::mado(id)->name;
        const std::shared_ptr<const Node> id_node = std::make_shared<const decltype(Identifier{std::string {"a"}})>(std::string {"a"}); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::make_shared<const decltype(Identifier{std::string {"a"}})>(std::string {"a"})), std::remove_cvref_t<decltype(id_node)>>);
        std::cout << ceto::mado(static_pointer_cast<std::type_identity_t<std::shared_ptr<const Identifier>> :: element_type>(id_node))->name;
        const std::vector<std::shared_ptr<const Node>> args = std::vector<std::shared_ptr<const Node>>{id, id_node}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<std::shared_ptr<const Node>>{id, id_node}), std::remove_cvref_t<decltype(args)>>);
        const auto args2 = std::vector<std::shared_ptr<const Node>>{id, id_node};
        static_cast<void>(args2);
        const auto node = std::make_shared<const decltype(Node{id, args})>(id, args);
        std::cout << (ceto::maybe_bounds_check_access(ceto::mado(node)->args,0) == nullptr);
        (std::cout << std::string {"\n"}) << ceto::mado(node)->repr();
        std::cout << ceto::mado(ceto::maybe_bounds_check_access(ceto::mado(node)->args,0))->repr();
    }

