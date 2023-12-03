
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


    template <typename T1, typename T2>
 static auto foo(const T1& x, const T2& y) -> int {
        return (x + y);
    }

     extern "C" inline auto foo2(const int  x, const int  y) -> int {
        return (x + y);
    }

    auto main() -> int {
        (std::cout << foo(1, 2)) << foo2(3, 4);
    }

