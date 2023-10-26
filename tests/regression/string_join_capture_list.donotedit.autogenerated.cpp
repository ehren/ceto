
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

#include <numeric>
;
    template <typename T1, typename T2>
auto join(const T1& v, const T2& to_string, const decltype(std::string {""})&  sep = std::string {""}) -> auto {
        return std::accumulate(ceto::mado(v)->begin() + 1, ceto::mado(v)->end(), to_string(ceto::maybe_bounds_check_access(v,0)), [&to_string = to_string, &sep](const auto &a, const auto &el) {
                if constexpr (!std::is_void_v<decltype(((a + sep) + to_string(el)))>) { return ((a + sep) + to_string(el)); } else { static_cast<void>(((a + sep) + to_string(el))); };
                });
    }

    auto main() -> int {
        const auto l = [](const auto &a) {
                if constexpr (!std::is_void_v<decltype(std::to_string(a))>) { return std::to_string(a); } else { static_cast<void>(std::to_string(a)); };
                };
        const auto csv = join(std::vector {{1, 2, 3, 4, 5}}, [&](const auto &a) {
                if constexpr (!std::is_void_v<decltype(l(a))>) { return l(a); } else { static_cast<void>(l(a)); };
                }, std::string {", "});
        const auto b = std::string {"blah"};
        const auto csv2 = join(std::vector {0}, [=](const auto &a) {
                if constexpr (!std::is_void_v<decltype((b + std::to_string(a)))>) { return (b + std::to_string(a)); } else { static_cast<void>((b + std::to_string(a))); };
                });
        (std::cout << csv) << csv2;
    }

