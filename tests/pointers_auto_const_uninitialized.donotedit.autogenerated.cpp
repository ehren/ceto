
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
 int val;
 int val_east;
        int * const a = (&val); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype((&val)), std::remove_cvref_t<decltype(a)>>);
        int * const a2 = (&val_east); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype((&val_east)), std::remove_cvref_t<decltype(a2)>>);
        (*a) = 5;
        (*a2) = 5;
    }

