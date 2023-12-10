
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


    template <typename T1, typename T2>
auto map(const T1& values, const T2& fun) -> auto {
        auto results { std::vector<decltype(fun(std::declval<std::ranges::range_value_t<decltype(values)>>()))>() } ;
        for(const auto& v : values) {
            (*ceto::mad(results)).push_back(fun(v));
        }
        return results;
    }

    inline auto foo(const int  x) -> auto {
        std::cout << x;
        return x;
    }

    template <typename T1>
auto foo_generic(const T1& x) -> auto {
        std::cout << x;
        return x;
    }

    auto main() -> int {
        const auto l = std::vector {{1, 2, 3, 4}};
        map(map(l, [](const auto &x) {
                std::cout << x;
                if constexpr (!std::is_void_v<decltype((x * 2))>) { return (x * 2); } else { static_cast<void>((x * 2)); };
                }), [](const auto &x) {
                std::cout << x;
                if constexpr (!std::is_void_v<decltype(x)>) { return x; } else { static_cast<void>(x); };
                });
        map(l, foo);
        map(l, [](const int  x) {
                if constexpr (!std::is_void_v<decltype(foo_generic(x))>) { return foo_generic(x); } else { static_cast<void>(foo_generic(x)); };
                });
        map(l, [](const auto &x) {
                if constexpr (!std::is_void_v<decltype(foo_generic(x))>) { return foo_generic(x); } else { static_cast<void>(foo_generic(x)); };
                });
        map(l, foo_generic<int>);
    }

