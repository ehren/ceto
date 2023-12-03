
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
        if (auto x { 5 } ) {
            x = 1;
        } else if (auto x { 2 } ) {
            x = 3;
        }
        const auto x = std::vector {{0, 1}};
    }

