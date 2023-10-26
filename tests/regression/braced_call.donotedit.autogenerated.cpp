
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
        const auto a = std::array<int,3>{1, 2, 3};
        const std::array<int,3> a3 = {1, 2, 3};
        const std::array<int,3> a4 = std::array<int,3>{1, 2, 3}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::array<int,3>{1, 2, 3}), std::remove_cvref_t<decltype(a4)>>);
        const auto v = std::vector<int>{1, 2};
        const auto v2 = std::vector<int>(30, 5);
        const std::vector<int> v3 = {30, 5};
        for(const auto& x : {a, a3, a4}) {
            for(const auto& i : x) {
                std::cout << i;
            }
        }
        for(const auto& x : {v, v2, v3}) {
            for(const auto& i : x) {
                std::cout << i;
            }
        }
        for(const auto& x : std::array{a, a3, a4}) {
            for(const auto& i : x) {
                std::cout << i;
            }
        }
        const auto get = [](const auto &t) -> void {
                (std::cout << ceto::maybe_bounds_check_access(std::get<0>(t),0));
                };
        const auto t = std::tuple{a, a3, a4, v, v2, v3};
        const auto t2 = std::make_tuple(a, v);
        get(t);
        get(t2);
    }

