
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
        auto y { 1 } ;
        const auto x = (y = 0);
        (std::cout << x) << y;
        const auto y2 = (y = x);
        static_assert(std::is_same_v<decltype(y2),const int>);
    }

