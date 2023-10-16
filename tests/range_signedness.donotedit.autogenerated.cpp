
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
        static_assert(std::is_same_v<std::remove_cvref_t<decltype(0)>, std::remove_cvref_t<decltype(10)>>);
        for (std::remove_cvref_t<decltype(0)> i = 0; i < 10; ++i) {
            static_assert(std::is_same_v<decltype(i),int>);
            std::cout << i;
        }
        const unsigned int u { 10 } ; static_assert(std::is_convertible_v<decltype(10), decltype(u)>);
        const unsigned int z { 0 } ; static_assert(std::is_convertible_v<decltype(0), decltype(z)>);
        static_assert(std::is_same_v<std::remove_cvref_t<decltype(z)>, std::remove_cvref_t<decltype(u)>>);
        for (std::remove_cvref_t<decltype(z)> i = z; i < u; ++i) {
            static_assert(std::is_same_v<decltype(i),int unsigned>);
            static_assert(std::is_same_v<decltype(i),unsigned int>);
            std::cout << i;
        }
    }

