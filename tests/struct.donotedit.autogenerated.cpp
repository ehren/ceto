
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

struct Foo : ceto::shared_object {

    std::string x;

    explicit Foo(std::string x) : x(x) {}

    Foo() = delete;

};

    inline auto by_const_ref(const Foo&  f) -> void {
        static_assert(std::is_same_v<decltype(f),const Foo &>);
        static_assert(std::is_reference_v<decltype(f)>);
        static_assert(std::is_const_v<std::remove_reference_t<decltype(f)>>);
        std::cout << ceto::mado(f)->x;
    }

    inline auto by_val( Foo  f) -> void {
        static_assert(std::is_same_v<decltype(f),Foo>);
        static_assert(!std::is_reference_v<decltype(f)>);
        static_assert(!std::is_const_v<std::remove_reference_t<decltype(f)>>);
        std::cout << ceto::mado(f)->x;
    }

    inline auto by_const_val( Foo const  f) -> void {
        static_assert(std::is_same_v<decltype(f),const Foo>);
        static_assert(!std::is_reference_v<decltype(f)>);
        static_assert(std::is_const_v<std::remove_reference_t<decltype(f)>>);
        std::cout << ceto::mado(f)->x;
    }

    inline auto by_mut_ref( Foo &  f) -> void {
        static_assert(std::is_same_v<decltype(f),Foo &>);
        static_assert(std::is_reference_v<decltype(f)>);
        static_assert(!std::is_const_v<std::remove_reference_t<decltype(f)>>);
        ceto::mado(f)->x += std::string {"hi"};
        std::cout << ceto::mado(f)->x;
    }

    inline auto by_ptr(const Foo *  f) -> void {
        static_assert(std::is_same_v<decltype(f),const Foo *>);
        static_assert(!std::is_reference_v<decltype(f)>);
        static_assert(!std::is_const_v<std::remove_reference_t<decltype(f)>>);
        static_assert(std::is_const_v<std::remove_reference_t<decltype(*f)>>);
        std::cout << (f -> x);
    }

    inline auto by_ptr_all_const( const Foo * const  f) -> void {
        static_assert(!std::is_reference_v<decltype(f)>);
        static_assert(std::is_const_v<std::remove_reference_t<decltype(f)>>);
        static_assert(std::is_const_v<std::remove_reference_t<decltype(*f)>>);
        std::cout << (f -> x);
    }

    inline auto by_ptr_mut( Foo *  f) -> void {
        static_assert(std::is_same_v<decltype(f),Foo *>);
        static_assert(!std::is_reference_v<decltype(f)>);
        static_assert(!std::is_const_v<std::remove_reference_t<decltype(f)>>);
        static_assert(!std::is_const_v<std::remove_reference_t<decltype(*f)>>);
        (f -> x) += std::string {"viaptr"};
        std::cout << (f -> x);
    }

    auto main() -> int {
        const auto f = decltype(Foo{std::string {"blah"}})(std::string {"blah"});
        by_const_ref(f);
        by_val(f);
        by_const_val(f);
        auto fm { f } ;
        by_mut_ref(fm);
        by_ptr((&f));
        by_ptr_all_const((&f));
        by_ptr_mut((&fm));
    }

