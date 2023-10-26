
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

    int a;

        inline auto mutmethod() -> auto {
            (this -> a) = ((this -> a) + 1);
            return (this -> a);
        }

        inline auto constmethod() const -> auto {
            return std::string {"i'm const by default"};
        }

    explicit Foo(int a) : a(a) {}

    Foo() = delete;

};

struct HolderMut : ceto::shared_object {

    std::shared_ptr<Foo> f;

    explicit HolderMut(std::shared_ptr<Foo> f) : f(f) {}

    HolderMut() = delete;

};

struct HolderConst : ceto::shared_object {

    std::shared_ptr<const Foo> f;

    explicit HolderConst(std::shared_ptr<const Foo> f) : f(f) {}

    HolderConst() = delete;

};

    auto main() -> int {
        const auto f = std::make_shared<const decltype(Foo{1})>(1);
        const auto h = std::make_shared<const decltype(HolderConst{f})>(f);
        std::cout << ceto::mado(ceto::mado(h)->f)->constmethod();
        auto fm { std::make_shared<decltype(Foo{2})>(2) } ;
        const auto hm = std::make_shared<const decltype(HolderMut{fm})>(fm);
        std::cout << ceto::mado(ceto::mado(hm)->f)->mutmethod();
        const auto hc = std::make_shared<const decltype(HolderConst{fm})>(fm);
        std::cout << ceto::mado(ceto::mado(hc)->f)->constmethod();
    }

