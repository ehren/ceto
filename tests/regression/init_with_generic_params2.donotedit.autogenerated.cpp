
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

    int x;

    int y;

    explicit Foo(const decltype(5) x = 5, const decltype(4) y = 4) : x(x), y(y) {
    }

};

    auto main() -> int {
        const auto f1 = std::make_shared<const decltype(Foo())>();
        const auto f2 = std::make_shared<const decltype(Foo{1})>(1);
        const auto f3 = std::make_shared<const decltype(Foo{2, 3})>(2, 3);
        for(const auto& f : {f1, f2, f3}) {
            (std::cout << ceto::mado(f)->x) << ceto::mado(f)->y;
        }
    }

