
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

};

    auto main() -> int {
        const auto f = std::make_shared<const decltype(Foo())>();
        static_assert(std::is_same_v<decltype(f),const std::shared_ptr<const Foo>>);
        std::shared_ptr<Foo> f1 = std::make_shared<decltype(Foo())>(); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::make_shared<decltype(Foo())>()), std::remove_cvref_t<decltype(f1)>>);
        static_assert(std::is_same_v<decltype(f1),std::shared_ptr<Foo>>);
        auto f2 { std::make_shared<decltype(Foo())>() } ;
        static_assert(std::is_same_v<decltype(f2),std::shared_ptr<Foo>>);
        auto f3 { std::make_shared<const decltype(Foo())>() } ;
        static_assert(std::is_same_v<decltype(f3),std::shared_ptr<const Foo>>);
        const auto f4 = std::make_shared<decltype(Foo())>();
        static_assert(std::is_same_v<decltype(f4),const std::shared_ptr<Foo>>);
        const auto f5 = std::make_shared<const decltype(Foo())>(); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::make_shared<const decltype(Foo())>()), std::remove_cvref_t<decltype(f5)>>);
        static_assert(std::is_same_v<decltype(f5),const std::shared_ptr<const Foo>>);
        const auto f6 = std::make_shared<const decltype(Foo())>(); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::make_shared<const decltype(Foo())>()), std::remove_cvref_t<decltype(f6)>>);
        static_assert(std::is_same_v<decltype(f6),const std::shared_ptr<const Foo>>);
        const auto f7 = std::make_shared<decltype(Foo())>(); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::make_shared<decltype(Foo())>()), std::remove_cvref_t<decltype(f7)>>);
        static_assert(std::is_same_v<decltype(f7),const std::shared_ptr<Foo>>);
        const std::shared_ptr<const Foo> f8 = std::make_shared<decltype(Foo())>(); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::make_shared<decltype(Foo())>()), std::remove_cvref_t<decltype(f8)>>);
        static_assert(std::is_same_v<decltype(f8),const std::shared_ptr<const Foo>>);
        const std::shared_ptr<const Foo> f9 = std::make_shared<const decltype(Foo())>(); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::make_shared<const decltype(Foo())>()), std::remove_cvref_t<decltype(f9)>>);
        static_assert(std::is_same_v<decltype(f9),const std::shared_ptr<const Foo>>);
        const std::shared_ptr<const Foo> f10 = std::make_shared<const decltype(Foo())>(); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::make_shared<const decltype(Foo())>()), std::remove_cvref_t<decltype(f10)>>);
        static_assert(std::is_same_v<decltype(f10),const std::shared_ptr<const Foo>>);
        const std::weak_ptr<const Foo> f11 = f; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(f), std::remove_cvref_t<decltype(f11)>>);
        static_assert(std::is_same_v<decltype(f11),const std::weak_ptr<const Foo>>);
        std::weak_ptr<Foo> f12 = f1; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(f1), std::remove_cvref_t<decltype(f12)>>);
        static_assert(std::is_same_v<decltype(f12),std::weak_ptr<Foo>>);
        std::weak_ptr<Foo> f13 = f1; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(f1), std::remove_cvref_t<decltype(f13)>>);
        static_assert(std::is_same_v<decltype(f13),std::weak_ptr<Foo>>);
        const std::weak_ptr<const Foo> f14 = f1; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(f1), std::remove_cvref_t<decltype(f14)>>);
        static_assert(std::is_same_v<decltype(f14),const std::weak_ptr<const Foo>>);
    }

