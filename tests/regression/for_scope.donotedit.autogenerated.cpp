
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
        const auto x = 5;
        auto l { std::vector {{1, 2, 3}} } ;
        for( auto &&  x : l) {
            x = (x + 1);
        }
        for(const auto& x : l) {
            printf("%d", x);
        }
        for( auto &&  x : std::vector {{1, 2, 3}}) {
            x = (x + 1);
            printf("%d", x);
        }
        printf("%d", x);
    }

