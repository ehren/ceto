
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
;
;
    auto main() -> int {
        const auto l = [&]() {
                auto result { std::vector<std::ranges::range_value_t<decltype(std::ranges::iota_view(0, 10))>>() } ;
                for(const auto& x : std::ranges::iota_view(0, 10)) {
                    if ((x % 2) == 0) {
                        (*ceto::mad(result)).push_back(x);
                    }
                }
                return result;
                }();
        for(const auto& x : l) {
            std::cout << x;
        }
        const auto l2 = [&]() {
                auto result { std::vector<decltype(std::declval<std::ranges::range_value_t<decltype(std::ranges::iota_view(0, 5))>>()+1)>() } ;
                for(const auto& x : std::ranges::iota_view(0, 5)) {
                    (*ceto::mad(result)).push_back(x + 1);
                }
                return result;
                }();
    }

