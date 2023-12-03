
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


struct C : public ceto::shared_object, public std::enable_shared_from_this<C> {

    int a;

    explicit C(int a) : a(a) {}

    C() = delete;

};

    inline auto foo(const std::shared_ptr<const C>&  c) -> void {
        ; // pass
    }

    inline auto bar( std::shared_ptr<const C>  c) -> void {
        ; // pass
    }

    inline auto byval(const std::type_identity_t<std::shared_ptr<const C>>  c) -> void {
        assert((&c) -> use_count() > 1);
        static_assert(std::is_same_v<const std::shared_ptr<std::type_identity_t<std::shared_ptr<const C>> :: element_type>,decltype(c)>);
        static_assert(std::is_same_v<const std::shared_ptr<std::remove_reference_t<decltype(*c)>>,decltype(c)>);
    }

    inline auto byconstref(const std::shared_ptr<const C>&  c) -> void {
        assert((&c) -> use_count() == 1);
        static_assert(std::is_reference_v<decltype(c)>);
    }

    auto main() -> int {
        const auto c = std::make_shared<const decltype(C{1})>(1);
        foo(c);
        bar(std::make_shared<const decltype(C{1})>(1));
        bar(c);
        const std::shared_ptr<const C> c2 = std::make_shared<const decltype(C{2})>(2); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::make_shared<const decltype(C{2})>(2)), std::remove_cvref_t<decltype(c2)>>);
        const std::shared_ptr<const C> c3 = c; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(c), std::remove_cvref_t<decltype(c3)>>);
        bar(c2);
        bar(c3);
        const auto c4 = std::make_shared<const decltype(C{1})>(1);
        byval(c4);
        byconstref(c4);
    }

