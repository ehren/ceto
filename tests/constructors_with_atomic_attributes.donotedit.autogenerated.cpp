
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

    std::atomic<int> a { 0 } ; static_assert(std::is_convertible_v<decltype(0), decltype(a)>);

};

struct Foo2 : ceto::shared_object {

    const std::atomic<int> a;

    explicit Foo2(const int  p) : a(p) {
    }

    Foo2() = delete;

};

    auto main() -> int {
        const auto f = std::make_shared<const decltype(Foo())>();
        const auto f2 = std::make_shared<const decltype(Foo2{1})>(1);
        static_assert(!std::is_const_v<decltype(ceto::mado(f)->a)>);
        static_assert(std::is_const_v<decltype(ceto::mado(f2)->a)>);
    }

