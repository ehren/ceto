
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

    inline auto is_void() -> void {
        ; // pass
    }

    auto main() -> int {
        const auto f = [](const auto &x) {
                (std::cout << x) << std::endl;
                if constexpr (!std::is_void_v<decltype(void())>) { return void(); } else { static_cast<void>(void()); };
                };
        f(1);
        static_assert(std::is_same_v<decltype(f(1)),void>);
        static_assert(std::is_same_v<decltype(is_void()),void>);
        const auto f2 = [](const auto &x) {
                if constexpr (!std::is_void_v<decltype(x)>) { return x; } else { static_cast<void>(x); };
                };
        (std::cout << f2(2)) << std::endl;
        static_assert(std::is_same_v<decltype(f2(2)),int>);
        const auto f3 = [](const auto &x) -> void {
                ((std::cout << x) << std::endl);
                };
        f3(3);
        static_assert(std::is_same_v<decltype(f3(3)),void>);
        const auto f4 = [](const auto &x) -> int {
                (std::cout << x) << std::endl;
                if constexpr (!std::is_void_v<decltype(x)>&& !std::is_void_v<int>) { return x; } else { static_cast<void>(x); };
                };
        (std::cout << f4(4)) << std::endl;
        static_assert(std::is_same_v<decltype(f4(4)),int>);
        const auto val = [](const auto &x) -> int {
                if constexpr (!std::is_void_v<decltype(x)>&& !std::is_void_v<int>) { return x; } else { static_cast<void>(x); };
                }(5);
        (std::cout << val) << std::endl;
    }

