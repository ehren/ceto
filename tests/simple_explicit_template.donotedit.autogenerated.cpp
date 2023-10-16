
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

     template<typename T,typename Y> inline auto foo( const T &  x,  const Y &  y) -> decltype(x * y) {
        return (x + y);
    }

     template<typename T,typename Y> inline auto foo(const T  x,  const Y &  y) -> std::enable_if_t<std::is_pointer_v<T>,decltype(x)> {
        return (x + y);
    }

    auto main() -> int {
        std::cout << foo(1, 2);
        const auto x = 5;
        const auto p = (&x);
        std::cout << (*foo(p, 0));
    }

