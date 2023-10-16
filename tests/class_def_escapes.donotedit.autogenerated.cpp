
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

        inline auto doit() const -> auto {
            printf("%d\n", 55 + 89);
            return 1;
        }

};

    template <typename T1>
auto huh(const T1& x) -> void {
        ceto::mado(x)->doit();
    }

    auto main() -> int {
        const auto f = std::make_shared<const decltype(Foo())>();
        huh(f);
        const auto o = f;
        huh(o);
        const auto l = std::vector {{f, o}};
    }

