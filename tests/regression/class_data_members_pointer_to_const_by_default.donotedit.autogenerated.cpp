
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


template <typename ceto__private__C1>struct Foo : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C1 a;

        inline auto mutmethod() -> auto {
            (this -> a) = ((this -> a) + 1);
            return (this -> a);
        }

        inline auto constmethod() const -> auto {
            return "i'm const by default";
        }

    explicit Foo(ceto__private__C1 a) : a(std::move(a)) {}

    Foo() = delete;

};

template <typename ceto__private__C2>struct Holder : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C2 f;

    explicit Holder(ceto__private__C2 f) : f(std::move(f)) {}

    Holder() = delete;

};

    auto main() -> int {
        const auto f = std::make_shared<const decltype(Foo{1})>(1);
        const auto h = std::make_shared<const decltype(Holder{f})>(f);
        std::cout << (*ceto::mad((*ceto::mad(h)).f)).constmethod();
        auto f2 { std::make_shared<decltype(Foo{2})>(2) } ;
        const auto h2 = std::make_shared<const decltype(Holder{f2})>(f2);
        std::cout << (*ceto::mad((*ceto::mad(h2)).f)).mutmethod();
    }

