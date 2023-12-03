
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
        const auto zz = std::vector {{1, 2, 3}};
        ceto::mad(x)->push_back(ceto::maybe_bounds_check_access(zz,1));
        std::cout << ceto::maybe_bounds_check_access(x,0);
    }

