
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

        inline auto mutmethod() -> auto {
            (this -> a) = ((this -> a) + 1);
            return (this -> a);
        }

        inline auto constmethod() const -> auto {
            return "i'm const by default";
        }

    explicit Foo(int a) : a(a) {}

    Foo() = delete;

};

struct HolderMut : public ceto::shared_object, public std::enable_shared_from_this<HolderMut> {

    std::shared_ptr<Foo> f;

    explicit HolderMut(std::shared_ptr<Foo> f) : f(std::move(f)) {}

    HolderMut() = delete;

};

struct HolderConst : public ceto::shared_object, public std::enable_shared_from_this<HolderConst> {

    std::shared_ptr<const Foo> f;

    explicit HolderConst(std::shared_ptr<const Foo> f) : f(std::move(f)) {}

    HolderConst() = delete;

};

    auto main() -> int {
        const auto f = std::make_shared<const decltype(Foo{1})>(1);
        const auto h = std::make_shared<const decltype(HolderConst{f})>(f);
        std::cout << (*ceto::mad((*ceto::mad(h)).f)).constmethod();
        auto fm { std::make_shared<decltype(Foo{2})>(2) } ;
        const auto hm = std::make_shared<const decltype(HolderMut{fm})>(fm);
        std::cout << (*ceto::mad((*ceto::mad(hm)).f)).mutmethod();
        const auto hc = std::make_shared<const decltype(HolderConst{fm})>(fm);
        std::cout << (*ceto::mad((*ceto::mad(hc)).f)).constmethod();
    }

