
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


    template <typename T1>
auto stuff(const T1& a) -> auto {
        return ceto::maybe_bounds_check_access(a,0);
    }

    template <typename T1, typename T2, typename T3>
auto takes_func_arg_arg(const T1& func, const T2& arg1, const T3& arg2) -> auto {
        return func(arg1, arg2);
    }

    template <typename T1>
auto foo(const T1& x) -> auto {
        return (x + 1);
    }

    auto main() -> int {
        auto x { std::vector<decltype(1)>() } ;
        const auto zz = std::vector {{1, 2, 3}};
        const auto xx = std::vector {{std::vector {{1, 2}}, std::vector {{2, 3}}}};
        auto xx2 { std::vector<std::vector<std::vector<int>>>() } ;
        auto xx3 { std::vector<std::vector<std::vector<decltype(1)>>>() } ;
        const auto xxanother = xx;
        std::vector<std::vector<int>> xxanother2 = xxanother; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(xxanother), std::remove_cvref_t<decltype(xxanother2)>>);
        auto xxanother3 { xxanother } ;
        (*ceto::mad(xx2)).push_back(xxanother2);
        (*ceto::mad(xx3)).push_back(xxanother3);
        ceto::maybe_bounds_check_access(xxanother2,0) = std::vector {{7, 7, 7}};
        ceto::maybe_bounds_check_access(xxanother3,1) = std::vector {{8, 7, 6}};
        printf("xxanother2 %d\n", ceto::maybe_bounds_check_access(ceto::maybe_bounds_check_access(xxanother2,0),0));
        printf("xxanother %d\n", ceto::maybe_bounds_check_access(ceto::maybe_bounds_check_access(xxanother,0),0));
        const auto lfunc = [](const auto &x, const auto &y) {
                return (x + y);
                };
        const auto lfunc2 = [](const auto &x, const auto &y) {
                printf("x %d y %d\n", x, y);
                return (x + y);
                };
        const auto huh = takes_func_arg_arg(lfunc2, 14, 15);
        printf("yo:\n            %d %d\n", ceto::maybe_bounds_check_access(ceto::maybe_bounds_check_access(ceto::maybe_bounds_check_access(xx3,0),0),0), huh);
        const auto z = 5;
        const auto w = z;
        const auto q = foo(w + 1);
        if (1) {
            (*ceto::mad(x)).push_back(ceto::maybe_bounds_check_access(zz,1));
        } else if ((z == 4)) {
            if (q == 6) {
                static_cast<void>(1);
            } else {
                static_cast<void>(10);
            }
        } else {
            (*ceto::mad(x)).push_back(foo(w - 1));
        }
        printf("ohsnap\n%d", ceto::maybe_bounds_check_access(x,0));
        const auto yy = std::vector {{ceto::maybe_bounds_check_access(x,0), foo(ceto::maybe_bounds_check_access(x,0))}};
        const auto y = std::vector {{ceto::maybe_bounds_check_access(x,0), foo(w), w + 25}};
        printf("ohsnap2 %d %d %d\n", stuff(y), ceto::maybe_bounds_check_access(y,1), ceto::maybe_bounds_check_access(yy,0));
        return 0;
    }

