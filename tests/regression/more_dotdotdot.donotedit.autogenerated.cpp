
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


     template<typename ... Types> inline auto count() -> auto {
        return sizeof...(Types);
    }

    auto main() -> int {
        (std :: cout) << count<int,float,char>();
    }

