
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


constexpr const auto g { 5 } ; static_assert(std::is_convertible_v<decltype(5), decltype(g)>);
    auto main() -> int {
        const auto c { 2 } ; static_assert(std::is_convertible_v<decltype(2), decltype(c)>);
        static_assert(std::is_const_v<decltype(c)>);
        static_assert(std::is_const_v<decltype(g)>);
        (std::cout << c) << g;
    }

