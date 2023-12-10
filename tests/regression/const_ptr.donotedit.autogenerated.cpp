
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

    int a;

        inline auto method() -> void {
            ; // pass
        }

    explicit Foo(int a) : a(a) {}

    Foo() = delete;

};

    template <typename T1>
auto calls_method(const T1& f) -> void {
        (*ceto::mad(f)).method();
    }

    auto main() -> int {
        const std::shared_ptr<const Foo> fc = std::make_shared<const decltype(Foo{1})>(1); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::make_shared<const decltype(Foo{1})>(1)), std::remove_cvref_t<decltype(fc)>>);
        const auto f { std::make_shared<decltype(Foo{1})>(1) } ;
        static_assert(std::is_const_v<decltype(f)>);
        (*ceto::mad(f)).method();
        calls_method(f);
    }

