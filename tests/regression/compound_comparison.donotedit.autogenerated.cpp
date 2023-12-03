
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



#include <array>
;
    auto main() -> int {
        if ((1 < 2) > 0) {
            std::cout << "yes";
        }
        const auto l = std::vector {{1, 2, 3}};
        const auto lp = (&l);
        if (0 < lp -> size()) {
            std::cout << "ok";
        }
         std::array<int,3> a;
        static_cast<void>(a);
         std::array<int,3> a2;
        static_cast<void>(a2);
        if (ceto::maybe_bounds_check_access(std::array<int,25>(),5)) {
            ; // pass
        }
        if (ceto::maybe_bounds_check_access(std::array<int,26>(),5)) {
            ; // pass
        }
        if (ceto::maybe_bounds_check_access(std::array<int,28>(),5)) {
            ; // pass
        }
        if (1 + ceto::maybe_bounds_check_access(std::array<int,29>(),5)) {
            ; // pass
        }
        const auto f = []() {
                return []() {
                        std::cout << "hi";
                        return;
                        };
                };
        const auto f2 = []() {
                return []() {
                        std::cout << "hi";
                        return;
                        };
                };
        f()();
        f2()();
        const auto fn = std::function([]() {
                if constexpr (!std::is_void_v<decltype("yo")>) { return "yo"; } else { static_cast<void>("yo"); };
                });
        const auto lf = std::vector {fn};
        std::cout << ceto::maybe_bounds_check_access(lf,0)();
    }

