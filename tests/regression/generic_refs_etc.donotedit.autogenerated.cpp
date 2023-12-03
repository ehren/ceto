
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
        const auto x = 1;
        const auto & xref { x } ;
        const auto y { 2 } ;
        const auto & z { 3 } ;
        const int & r = xref; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(xref), std::remove_cvref_t<decltype(r)>>);
        int const & r2 = xref; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(xref), std::remove_cvref_t<decltype(r2)>>);
        const auto * p { (&x) } ;
        const auto * * p2 { (&p) } ;
        int const * const p3 = (&x); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype((&x)), std::remove_cvref_t<decltype(p3)>>);
    }

