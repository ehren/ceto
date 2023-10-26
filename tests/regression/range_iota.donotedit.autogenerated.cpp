
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
            std::cout << i;
        }
        static_assert(std::is_same_v<std::remove_cvref_t<decltype(0)>, std::remove_cvref_t<decltype(10)>>);
        for (std::remove_cvref_t<decltype(0)> i = 0; i < 10; ++i) {
            std::cout << i;
        }
        static_assert(std::is_same_v<std::remove_cvref_t<decltype((-10))>, std::remove_cvref_t<decltype(10)>>);
        for (std::remove_cvref_t<decltype((-10))> i = (-10); i < 10; ++i) {
            std::cout << i;
        }
    }

