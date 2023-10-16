
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

        inline auto method() const -> void {
            printf("no this");
        }

};

    auto main() -> int {
        auto f { std::make_shared<decltype(Foo())>() } ;
        f = nullptr;
        ceto::mado(f)->method();
    }

