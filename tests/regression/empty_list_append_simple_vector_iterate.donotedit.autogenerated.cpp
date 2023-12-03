
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


    auto main() -> int {
        auto v { std::vector<std::ranges::range_value_t<std::vector<decltype(0)>>>() } ;
        auto v2 { std::vector<std::ranges::range_value_t<decltype(v)>>() } ;
        const auto range = std::vector {{0, 1, 2}};
        for(const auto& x : range) {
            ceto::mad(v)->push_back(x);
        }
        for(const auto& x : std::vector {{0, 1, 2}}) {
            ceto::mad(v)->push_back(x);
        }
        for(const auto& x : v) {
            ceto::mad(v2)->push_back(x);
            ceto::mad(v2)->push_back(x);
        }
        for(const auto& x : v2) {
            std::cout << x;
        }
    }

