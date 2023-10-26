
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
        const auto [x, y] = std::make_tuple(0, 1);
        std::cout << x;
        std::cout << y;
        static_assert(std::is_same_v<decltype(x),const int>);
        static_assert(std::is_same_v<decltype(y),const int>);
    }

