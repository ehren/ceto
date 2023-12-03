
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
        const std::u8string u = u8"1"; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(u8"1"), std::remove_cvref_t<decltype(u)>>);
        const auto s = std::string(ceto::mado(u)->begin(), ceto::mado(u)->end());
        std::cout << s;
    }

