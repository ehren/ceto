
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
        const auto val = [](const auto &x) -> int {
                if constexpr (!std::is_void_v<decltype(x)>&& !std::is_void_v<int>) { return x; } else { static_cast<void>(x); };
                }(5);
        std::cout << val;
        const auto val2 = [](const auto &x) -> const char * {
                if constexpr (!std::is_void_v<decltype("hi")>&& !std::is_void_v<const char *>) { return "hi"; } else { static_cast<void>("hi"); };
                }(5);
        std::cout << val2;
    }

