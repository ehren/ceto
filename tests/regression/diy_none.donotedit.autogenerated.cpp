
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


constexpr const auto None2 = nullptr;
constexpr auto const None3 { nullptr } ;
    auto main() -> int {
        (std::cout << None2) << None3;
        static_assert(std::is_const_v<decltype(None2)>);
        static_assert(std::is_const_v<decltype(None3)>);
        static_assert(std::is_same_v<decltype(None2),const std::nullptr_t>);
    }

