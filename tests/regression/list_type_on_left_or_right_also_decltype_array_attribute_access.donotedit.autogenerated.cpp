
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

    std::vector<int> a;

    std::vector<int> b = std::vector<int>{1, 2, 3}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<int>{1, 2, 3}), std::remove_cvref_t<decltype(b)>>);

    decltype(std::vector<int>{1, 2, 3}) c = std::vector<int>{1, 2, 3};

    decltype(std::vector {{1, 2, 3}}) d = std::vector {{1, 2, 3}};

    explicit Foo(std::vector<int> a) : a(std::move(a)) {}

    Foo() = delete;

};

    auto main() -> int {
        const std::vector<int> x = std::vector<int>{1, 2, 3}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<int>{1, 2, 3}), std::remove_cvref_t<decltype(x)>>);
        const auto l1 = std::vector {std::make_shared<const decltype(Foo{x})>(x)};
        auto lm { std::vector<std::remove_cvref_t<decltype(ceto::mad(std::declval<std::remove_cvref_t<std::ranges::range_value_t<std::vector<std::vector<std::shared_ptr<const decltype(Foo{std::declval<std::vector<int>>()})>>>>>::value_type>())->a)>::value_type>() } ;
        auto lm2 { std::vector<std::remove_cvref_t<decltype(ceto::mad(std::declval<std::shared_ptr<const decltype(Foo{std::declval<std::vector<int>>()})>>())->a)>::value_type>() } ;
        auto lm3 { std::vector<std::remove_cvref_t<decltype(ceto::mad(std::declval<std::shared_ptr<const decltype(Foo{std::declval<std::vector<int>>()})>>())->a)>::value_type>() } ;
        auto lm4 { std::vector<std::remove_cvref_t<decltype(ceto::mad(std::declval<std::remove_cvref_t<std::ranges::range_value_t<std::vector<std::vector<std::shared_ptr<const decltype(Foo{std::declval<std::vector<int>>()})>>>>>::value_type>())->a)>::value_type>() } ;
        auto lm5 { std::vector<std::remove_cvref_t<decltype(ceto::mad(std::declval<std::remove_cvref_t<std::ranges::range_value_t<std::vector<std::vector<std::shared_ptr<const decltype(Foo{std::declval<std::vector<int>>()})>>>>>::value_type>())->a)>::value_type>() } ;
        auto lm6 { std::vector<std::remove_cvref_t<decltype(ceto::mad(std::declval<std::shared_ptr<const decltype(Foo{std::declval<std::vector<int>>()})>>())->a)>::value_type>() } ;
        auto lm8 { std::vector<std::remove_cvref_t<std::ranges::range_value_t<std::vector<std::vector<std::shared_ptr<const decltype(Foo{std::declval<std::vector<int>>()})>>>>>::value_type>() } ;
        auto lm7 { std::vector<std::remove_cvref_t<std::ranges::range_value_t<std::vector<std::vector<std::shared_ptr<const decltype(Foo{std::declval<std::vector<int>>()})>>>>>::value_type>() } ;
        auto lm9 { std::vector<std::remove_cvref_t<std::ranges::range_value_t<std::vector<std::vector<std::shared_ptr<const decltype(Foo{std::declval<std::vector<int>>()})>>>>>::value_type>() } ;
        const auto l2 = std::vector<std::shared_ptr<const Foo>>{std::make_shared<const decltype(Foo{x})>(x)};
        const std::vector<std::shared_ptr<const Foo>> l3 = std::vector<std::shared_ptr<const Foo>>{std::make_shared<const decltype(Foo{x})>(x)}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<std::shared_ptr<const Foo>>{std::make_shared<const decltype(Foo{x})>(x)}), std::remove_cvref_t<decltype(l3)>>);
        for(const auto& l : std::vector {{l1, l2, l3}}) {
            ceto::mad(lm)->push_back(ceto::maybe_bounds_check_access(ceto::mado(ceto::maybe_bounds_check_access(l,0))->a,2));
            ceto::mad(lm2)->push_back(ceto::maybe_bounds_check_access(ceto::mado(ceto::maybe_bounds_check_access(l3,0))->a,2));
            const auto a = ceto::maybe_bounds_check_access(ceto::mado(ceto::maybe_bounds_check_access(l1,0))->a,2);
            ceto::mad(lm3)->push_back(a);
            const auto b = ceto::maybe_bounds_check_access(ceto::mado(ceto::maybe_bounds_check_access(l,0))->a,2);
            ceto::mad(lm4)->push_back(b);
            ceto::mad(lm5)->push_back(ceto::maybe_bounds_check_access(lm,0));
            ceto::mad(lm6)->push_back(ceto::maybe_bounds_check_access(lm2,0));
            ceto::mad(lm7)->push_back(ceto::maybe_bounds_check_access(l,0));
            ceto::mad(lm8)->push_back(ceto::maybe_bounds_check_access(lm7,0));
            const auto c = l;
            ceto::mad(lm9)->push_back(ceto::maybe_bounds_check_access(c,0));
        }
        (((((std::cout << ceto::maybe_bounds_check_access(lm,0)) << ceto::maybe_bounds_check_access(lm2,0)) << ceto::maybe_bounds_check_access(lm4,0)) << ceto::maybe_bounds_check_access(ceto::mado(ceto::maybe_bounds_check_access(lm7,0))->a,0)) << ceto::maybe_bounds_check_access(ceto::mado(ceto::maybe_bounds_check_access(lm8,0))->b,1)) << ceto::maybe_bounds_check_access(ceto::mado(ceto::maybe_bounds_check_access(lm9,0))->c,2);
    }

