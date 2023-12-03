
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
        const auto x = [&]() {if (1) {
            return std::vector {{1, 2}};
        } else {
            return std::vector {{2, 1}};
        }}()
;
        (std::cout << ceto::maybe_bounds_check_access(x,0)) << ceto::maybe_bounds_check_access(x,1);
        std::cout << [&]() {if (1) {
            return 2;
        } else {
            return 1;
        }}()
;
    }

