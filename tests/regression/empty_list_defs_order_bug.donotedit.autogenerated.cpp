
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

#define AUTO auto
;
    auto main() -> int {
        auto result { std::vector<std::ranges::range_value_t<decltype(std::ranges::iota_view(0, 10))>>() } ;
        auto && z { std::ranges::iota_view(0, 10) } ;
        for(const auto& y : z) {
            (*ceto::mad(result)).push_back(y);
        }
        std::cout << (*ceto::mad(result)).size();
    }

