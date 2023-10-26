
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

template <typename _ceto_private_C1>struct Foo : ceto::shared_object {

    _ceto_private_C1 a;

        inline auto mutmethod() -> auto {
            (this -> a) = ((this -> a) + 1);
            return (this -> a);
        }

        inline auto constmethod() const -> auto {
            return std::string {"i'm const by default"};
        }

    explicit Foo(_ceto_private_C1 a) : a(a) {}

    Foo() = delete;

};

template <typename _ceto_private_C2>struct Holder : ceto::shared_object {

    _ceto_private_C2 f;

    explicit Holder(_ceto_private_C2 f) : f(f) {}

    Holder() = delete;

};

    auto main() -> int {
        const auto f = std::make_shared<const decltype(Foo{1})>(1);
        const auto h = std::make_shared<const decltype(Holder{f})>(f);
        std::cout << ceto::mado(ceto::mado(h)->f)->constmethod();
        auto f2 { std::make_shared<decltype(Foo{2})>(2) } ;
        const auto h2 = std::make_shared<const decltype(Holder{f2})>(f2);
        std::cout << ceto::mado(ceto::mado(h2)->f)->mutmethod();
    }

