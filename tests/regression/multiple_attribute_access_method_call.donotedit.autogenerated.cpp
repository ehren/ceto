
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

struct Foo : public ceto::shared_object, public std::enable_shared_from_this<Foo> {

    std::shared_ptr<const Foo> f;

        inline auto use_count() const -> auto {
            const auto self = ceto::shared_from(this);
            return (&self) -> use_count();
        }

    explicit Foo(std::shared_ptr<const Foo> f) : f(std::move(f)) {}

    Foo() = delete;

};

struct FooList : public ceto::shared_object, public std::enable_shared_from_this<FooList> {

    std::vector<std::shared_ptr<const Foo>> l = std::vector<std::shared_ptr<const Foo>>{}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<std::shared_ptr<const Foo>>{}), std::remove_cvref_t<decltype(l)>>);

};

    auto main() -> int {
        const auto f = std::make_shared<const decltype(Foo{std::make_shared<const decltype(Foo{std::make_shared<const decltype(Foo{std::make_shared<const decltype(Foo{std::make_shared<const decltype(Foo{nullptr})>(nullptr)})>(std::make_shared<const decltype(Foo{nullptr})>(nullptr))})>(std::make_shared<const decltype(Foo{std::make_shared<const decltype(Foo{nullptr})>(nullptr)})>(std::make_shared<const decltype(Foo{nullptr})>(nullptr)))})>(std::make_shared<const decltype(Foo{std::make_shared<const decltype(Foo{std::make_shared<const decltype(Foo{nullptr})>(nullptr)})>(std::make_shared<const decltype(Foo{nullptr})>(nullptr))})>(std::make_shared<const decltype(Foo{std::make_shared<const decltype(Foo{nullptr})>(nullptr)})>(std::make_shared<const decltype(Foo{nullptr})>(nullptr))))})>(std::make_shared<const decltype(Foo{std::make_shared<const decltype(Foo{std::make_shared<const decltype(Foo{std::make_shared<const decltype(Foo{nullptr})>(nullptr)})>(std::make_shared<const decltype(Foo{nullptr})>(nullptr))})>(std::make_shared<const decltype(Foo{std::make_shared<const decltype(Foo{nullptr})>(nullptr)})>(std::make_shared<const decltype(Foo{nullptr})>(nullptr)))})>(std::make_shared<const decltype(Foo{std::make_shared<const decltype(Foo{std::make_shared<const decltype(Foo{nullptr})>(nullptr)})>(std::make_shared<const decltype(Foo{nullptr})>(nullptr))})>(std::make_shared<const decltype(Foo{std::make_shared<const decltype(Foo{nullptr})>(nullptr)})>(std::make_shared<const decltype(Foo{nullptr})>(nullptr)))));
        std::cout << ceto::mado(ceto::mado(ceto::mado(ceto::mado(ceto::mado(f)->f)->f)->f)->f)->use_count();
        ceto::mado(ceto::mado(std::make_shared<decltype(FooList())>())->l)->push_back(f);
        ceto::mado(std::make_shared<const decltype(FooList())>())->l;
        std::cout << ceto::mado(ceto::mado(std::make_shared<const decltype(Foo{std::make_shared<const decltype(Foo{nullptr})>(nullptr)})>(std::make_shared<const decltype(Foo{nullptr})>(nullptr)))->f)->use_count();
        std::cout << ceto::mado(ceto::mado(std::make_shared<const decltype(Foo{std::make_shared<const decltype(Foo{nullptr})>(nullptr)})>(std::make_shared<const decltype(Foo{nullptr})>(nullptr)))->f)->use_count();
        ceto::mad(ceto::mado(std::make_shared<const decltype(FooList())>())->l)->operator[](0);
        auto fl { std::make_shared<decltype(FooList())>() } ;
        ceto::mado(ceto::mado(fl)->l)->push_back(f);
        std::cout << ceto::mado(ceto::mad(ceto::mado(fl)->l)->operator[](0))->use_count();
    }

