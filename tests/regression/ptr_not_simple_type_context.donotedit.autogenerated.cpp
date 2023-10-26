
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
        const auto x = 0;
        auto xmut { 0 } ;
        const int * const y = (&x); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype((&x)), std::remove_cvref_t<decltype(y)>>);
 int * y2;
        y2 = (&xmut);
 int * y3;
        y3 = (&xmut);
        const auto hmm = reinterpret_cast<int *>(1);
        static_cast<void>(y);
        static_cast<void>(y2);
        static_cast<void>(y3);
        static_assert(!std::is_same_v<decltype(nullptr),int *>);
        printf("%p", static_cast<void *>(hmm));
    }

