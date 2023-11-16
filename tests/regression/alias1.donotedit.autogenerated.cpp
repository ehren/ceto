
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

        ~Foo() {
            std::cout << "Foo destruct";
        }

};

    template <typename T2>
auto aliaser( auto &  f, const T2& g) -> void {
        std::cout << "in aliaser";
        f = nullptr;
        std::cout << (&g) -> use_count();
        std::cout << ((&g) -> get() == nullptr);
        std::cout << (g == nullptr);
    }

    auto main() -> int {
        auto f { std::make_shared<decltype(Foo())>() } ;
        aliaser(f, f);
    }

