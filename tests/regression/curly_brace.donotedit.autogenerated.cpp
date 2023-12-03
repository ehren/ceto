
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
        const std::vector<std::vector<int>> l = {{1}, {1, 2, 3}};
        const std::vector<std::vector<int>> l2 = {{1, 2}};
        const std::vector<std::vector<int>> l3 = {{1}};
        const std::vector<std::vector<int>> l4 = {};
        const std::vector<int> a = {5, 2};
        const std::vector<std::vector<int>> a2 = {l};
        const std::vector<std::vector<int>> a3 = l; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(l), std::remove_cvref_t<decltype(a3)>>);
        const std::vector<std::vector<int>> a4 = {{l}};
        assert((((2 == ceto::mado(a)->size()) && (2 == ceto::mado(a2)->size())) && (2 == ceto::mado(a3)->size())) && (2 == ceto::mado(a4)->size()));
        for(const auto& ll : std::vector {{l, l2, l3, l4, a2}}) {
            for(const auto& li : ll) {
                for(const auto& lk : li) {
                    std::cout << lk;
                }
            }
        }
        std::cout << ceto::maybe_bounds_check_access(ceto::maybe_bounds_check_access(l3,0),0);
        const std::array<int,4> arr = {{1, 2, 3, 4}};
        const std::array<int,2> arr2 = {1, 2};
        const std :: array<std :: array<int,3>,2> arr3 = {{{{1, 2, 3}}, {{4, 5, 6}}}};
        const std :: array<std :: array<int,3>,2> arr4 = {{{1, 2, 3}}};
        const std :: array<std :: array<int,3>,2> arr8 = {{{{1}}}};
        std::cout << ceto::maybe_bounds_check_access(arr,3);
        std::cout << ceto::maybe_bounds_check_access(arr2,1);
        for(const auto& ll : std::vector {{arr3, arr4}}) {
            std::cout << ceto::maybe_bounds_check_access(ceto::maybe_bounds_check_access(ll,0),0);
        }
        const auto v = std::vector<int>(5, 42);
        std::cout << ceto::maybe_bounds_check_access(v,4);
        assert(ceto::mado(v)->size() == 5);
        const auto v2 = std::vector<int>{5, 42};
        assert(ceto::mado(v2)->size() == 2);
        const std::vector<int> vv = std::vector<int>(5, 42); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<int>(5, 42)), std::remove_cvref_t<decltype(vv)>>);
        std::cout << ceto::maybe_bounds_check_access(v,4);
        assert(ceto::mado(v)->size() == 5);
        const std::vector<int> vv2 = std::vector<int>{5, 42}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<int>{5, 42}), std::remove_cvref_t<decltype(vv2)>>);
        assert(ceto::mado(v2)->size() == 2);
        const std::vector<int> v1 = {1, 2};
        const std::vector<std::vector<int>> vv1 = {v};
    }

