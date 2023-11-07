
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

constexpr const int g { 5 } ; static_assert(std::is_convertible_v<decltype(5), decltype(g)>);
struct Foo : public ceto::shared_object, public std::enable_shared_from_this<Foo> {

    int a = []() {
            if constexpr (!std::is_void_v<decltype((5 + g))>) { return (5 + g); } else { static_cast<void>((5 + g)); };
            }(); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype([]() {
            if constexpr (!std::is_void_v<decltype((5 + g))>) { return (5 + g); } else { static_cast<void>((5 + g)); };
            }()), std::remove_cvref_t<decltype(a)>>);

    std::conditional_t<false,decltype([](const auto &x) {
            if constexpr (!std::is_void_v<decltype((x + g))>) { return (x + g); } else { static_cast<void>((x + g)); };
            }),int> f;

    explicit Foo(std::conditional_t<false,decltype([](const auto &x) {
            if constexpr (!std::is_void_v<decltype((x + g))>) { return (x + g); } else { static_cast<void>((x + g)); };
            }),int> f) : f(f) {}

    Foo() = delete;

};

constexpr const auto cg = "it's a global, no need to capture";
    auto main() -> int {
        const auto f = std::make_shared<const decltype(Foo{2})>(2);
        const auto l = [f = ceto::default_capture(f)]() {
                if constexpr (!std::is_void_v<decltype((g + ceto::mado(f)->a))>) { return (g + ceto::mado(f)->a); } else { static_cast<void>((g + ceto::mado(f)->a)); };
                };
        const auto l2 = []() {
                if constexpr (!std::is_void_v<decltype(cg)>) { return cg; } else { static_cast<void>(cg); };
                };
        ((((std::cout << ceto::mado(f)->f) << ceto::mado(f)->a) << l()) << std::string {"\n"}) << l2();
    }

