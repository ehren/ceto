
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


#include <iostream>
;
    auto main() -> int {
        const auto l { [](const auto &x) {
                if constexpr (!std::is_void_v<decltype((x + 1))>) { return (x + 1); } else { static_cast<void>((x + 1)); };
                } } ;
        auto const l2 { [](const auto &x) -> int {
                if constexpr (!std::is_void_v<decltype((x * 2))>&& !std::is_void_v<int>) { return (x * 2); } else { static_cast<void>((x * 2)); };
                } } ;
        const auto l3 = [](const auto &x) {
                if constexpr (!std::is_void_v<decltype((x * 3))>) { return (x * 3); } else { static_cast<void>((x * 3)); };
                };
        auto lmut { [](const auto &x) {
                if constexpr (!std::is_void_v<decltype((x * 4))>) { return (x * 4); } else { static_cast<void>((x * 4)); };
                } } ;
        (std::cout << l(2)) << l2(2);
        std::cout << std::is_const_v<decltype(l)>;
        std::cout << std::is_const_v<decltype(l2)>;
        std::cout << std::is_const_v<decltype(l3)>;
        std::cout << !std::is_const_v<decltype(lmut)>;
    }

