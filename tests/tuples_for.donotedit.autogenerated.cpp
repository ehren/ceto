
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

#include <ranges>
;
#include <iostream>
;
    inline auto foo(const std::tuple<int, int>&  tuple1, const decltype(std::make_tuple(0, 1)) tuple2 = std::make_tuple(0, 1)) -> auto {
        return std::make_tuple(std::get<0>(tuple1), std::get<1>(tuple2));
    }

    auto main() -> int {
        auto tuples { std::vector<decltype(std::make_tuple(std::declval<std::ranges::range_value_t<decltype(std::ranges::iota_view(0, 10))>>(), std::declval<std::ranges::range_value_t<decltype(std::ranges::iota_view(0, 10))>>()+1))>() } ;
        for(const auto& i : std::ranges::iota_view(0, 10)) {
            ceto::mad(tuples)->push_back(std::make_tuple(i, i + 1));
        }
        const auto [a, b] = std::make_tuple(ceto::maybe_bounds_check_access(tuples,0), ceto::maybe_bounds_check_access(tuples,1));
        ceto::mad(tuples)->push_back(a);
        std::tie(ceto::maybe_bounds_check_access(tuples,4), ceto::maybe_bounds_check_access(tuples,6)) = std::make_tuple(std::make_tuple(0, 0), b);
        std::tie(std::get<0>(ceto::maybe_bounds_check_access(tuples,7)), std::get<1>(ceto::maybe_bounds_check_access(tuples,7))) = foo(ceto::maybe_bounds_check_access(tuples,7));
        for(  const auto& [x, y] : tuples) {
            ((std::cout << x) << y) << "\n";
        }
    }

