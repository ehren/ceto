
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

    inline auto foo(const decltype(std::function([](const int  x) {
            if constexpr (!std::is_void_v<decltype(0)>) { return 0; } else { static_cast<void>(0); };
            })) f = [](const int  x) {
            if constexpr (!std::is_void_v<decltype(0)>) { return 0; } else { static_cast<void>(0); };
            }) -> auto {
        return f(3);
    }

    inline auto foo2(const decltype(std::function([](const int  x) -> int {
            if constexpr (!std::is_void_v<decltype(0)>&& !std::is_void_v<int>) { return 0; } else { static_cast<void>(0); };
            })) f = [](const int  x) -> int {
            if constexpr (!std::is_void_v<decltype(0)>&& !std::is_void_v<int>) { return 0; } else { static_cast<void>(0); };
            }) -> auto {
        return f(3);
    }

    inline auto foo3(const std::add_const_t<decltype(std::function([](const int  x) -> int {
            if constexpr (!std::is_void_v<decltype(0)>&& !std::is_void_v<int>) { return 0; } else { static_cast<void>(0); };
            }))> f = [](const int  x) -> int {
            if constexpr (!std::is_void_v<decltype(0)>&& !std::is_void_v<int>) { return 0; } else { static_cast<void>(0); };
            }) -> auto {
        static_assert(std::is_const_v<decltype(f)>);
        return f(3);
    }

    auto main() -> int {
        const auto l = [](const int  x) {
                std::cout << ("hi" + std::to_string(x));
                if constexpr (!std::is_void_v<decltype(5)>) { return 5; } else { static_cast<void>(5); };
                };
        const std::function f = l; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(l), std::remove_cvref_t<decltype(f)>>);
        const auto v = std::vector {f};
        (std::cout << ceto::maybe_bounds_check_access(v,0)(5)) << "\n";
        (std::cout << foo()) << "\n";
        (std::cout << foo(l)) << "\n";
        (std::cout << foo2()) << "\n";
        (std::cout << foo2(l)) << "\n";
        (std::cout << foo3()) << "\n";
        std::cout << foo3(l);
    }

