
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
    auto main() -> int {
        auto tuples { std::vector<decltype(std::make_tuple(std::declval<std::ranges::range_value_t<decltype(std::ranges::iota_view(0, 10))>>(), std::declval<std::ranges::range_value_t<decltype(std::ranges::iota_view(0, 10))>>()+1))>() } ;
        for(const auto& i : std::ranges::iota_view(0, 10)) {
            ceto::mad(tuples)->push_back(std::make_tuple(i, i + 1));
        }
        for(  const auto& [x, y] : tuples) {
            ((std::cout << x) << y) << std::string {"\n"};
        }
    }

