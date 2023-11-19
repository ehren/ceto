
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
        const auto & x { 1 } ;
        const int & y = x; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(x), std::remove_cvref_t<decltype(y)>>);
        auto const & z { y } ;
        static_assert(std::is_reference_v<decltype(x)>);
        static_assert(std::is_reference_v<decltype(y)>);
        static_assert(std::is_reference_v<decltype(z)>);
        static_assert(std::is_const_v<std::remove_reference_t<decltype(x)>>);
        static_assert(std::is_const_v<std::remove_reference_t<decltype(y)>>);
        static_assert(std::is_const_v<std::remove_reference_t<decltype(z)>>);
    }

