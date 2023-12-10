
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
        auto x { std::vector<decltype(1)>() } ;
        const auto lfunc = [](const auto &x, const auto &y) {
                if constexpr (!std::is_void_v<decltype((x + y))>) { return (x + y); } else { static_cast<void>((x + y)); };
                };
        (*ceto::mad(x)).push_back(1);
        std::cout << lfunc(ceto::maybe_bounds_check_access(x,0), ceto::maybe_bounds_check_access(x,0));
    }

