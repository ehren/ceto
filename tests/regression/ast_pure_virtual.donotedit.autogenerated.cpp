
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
struct Node : public ceto::shared_object, public std::enable_shared_from_this<Node> {

    std::shared_ptr<const Node> func;

    std::vector<std::shared_ptr<const Node>> args;

         virtual auto repr() const -> std::string = 0;

         virtual inline auto name() const -> std::optional<std::string> {
            return nullptr;
        }

    explicit Node(std::shared_ptr<const Node> func, std::vector<std::shared_ptr<const Node>> args) : func(std::move(func)), args(std::move(args)) {}

    Node() = delete;

};

struct Identifier : public Node {

    std::string _name;

        inline auto repr() const -> decltype(ceto::mado(static_cast<std::shared_ptr<const Node>>(nullptr))->repr()) {
            return (this -> _name);
        }

         virtual inline auto name() const -> decltype(ceto::mado(std::declval<std::shared_ptr<const Node>>())->name()) {
            return (this -> _name);
        }

    explicit Identifier(const std::string&  name) : Node (nullptr, std::vector<std::shared_ptr<const Node>>{}), _name(name) {
    }

    Identifier() = delete;

};

    inline auto example_macro_body_workaround_no_fptr_syntax_yet(const std::map<std::string,std::shared_ptr<const Node>>  matches) -> std::shared_ptr<const Node> {
        return nullptr;
    }

constexpr const auto glob = 0;
    inline auto macro_trampoline(const uintptr_t  fptr, const std::map<std::string,std::shared_ptr<const Node>>  matches) -> auto {
        const auto f = reinterpret_cast<decltype(+[](const std::map<std::string,std::shared_ptr<const Node>>  matches) -> std::shared_ptr<const Node> {
                if constexpr (!std::is_void_v<decltype(nullptr)>&& !std::is_void_v<std::shared_ptr<const Node>>) { return nullptr; } else { static_cast<void>(nullptr); };
                })>(fptr);
        const auto f2 = reinterpret_cast<decltype(+[](const std::map<std::string,std::shared_ptr<const Node>>  matches) -> std::shared_ptr<const Node> {
                if constexpr (!std::is_void_v<decltype(nullptr)>&& !std::is_void_v<std::shared_ptr<const Node>>) { return nullptr; } else { static_cast<void>(nullptr); };
                })>(0);
        const auto f3 = reinterpret_cast<decltype(+[](const std::map<std::string,std::shared_ptr<const Node>>  matches) -> std::shared_ptr<const Node> {
                if constexpr (!std::is_void_v<decltype(nullptr)>&& !std::is_void_v<std::shared_ptr<const Node>>) { return nullptr; } else { static_cast<void>(nullptr); };
                })>(glob);
        const auto f4 = (&example_macro_body_workaround_no_fptr_syntax_yet);
        static_assert(std::is_same_v<decltype(f),decltype(f2)>);
        static_assert(std::is_same_v<decltype(f),decltype(f3)>);
        static_assert(std::is_same_v<decltype(f),decltype(f4)>);
        return (*f)(matches);
    }

    auto main() -> int {
        const auto id = std::make_shared<const decltype(Identifier{"a"})>("a");
        std::cout << ceto::mad(ceto::mado(id)->name())->value();
    }

