
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


#include "ceto.h"


;

;

;

;

;

;

;

;

;

;

;
#include "ceto_private_listcomp.donotedit.autogenerated.h"
;
#include "ceto_private_boundscheck.donotedit.autogenerated.h"
;
#include "ceto_private_convenience.donotedit.autogenerated.h"
;
#include "ceto_private_append_to_pushback.donotedit.autogenerated.h"
;
#include <numeric>
;
    template <typename T1, typename T2>
auto join(const T1& v, const T2& to_string, const decltype(std::string {""})&  sep = std::string {""}) -> auto {
        return std::accumulate(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(v)).begin()) + 1, [&]() -> decltype(auto) { static_assert(((!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(v)).end()))>  || (!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(v)).begin()) + 1)> && std::is_fundamental_v<std::remove_cvref_t<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(v)).begin()) + 1)>> && !std::is_reference_v<decltype(to_string([&]() -> decltype(auto) { static_assert(((!std::is_reference_v<decltype(ceto::bounds_check(v, 0))> ) && ceto::IsStateless<std::remove_cvref_t<decltype(to_string)>>)); return ceto::bounds_check(v, 0); }()))> && std::is_fundamental_v<std::remove_cvref_t<decltype(to_string([&]() -> decltype(auto) { static_assert(((!std::is_reference_v<decltype(ceto::bounds_check(v, 0))> ) && ceto::IsStateless<std::remove_cvref_t<decltype(to_string)>>)); return ceto::bounds_check(v, 0); }()))>> && !std::is_reference_v<decltype([&to_string = to_string, &sep](const auto &a, const auto &el) {
                return ((a + sep) + to_string(el));
                })> && std::is_fundamental_v<std::remove_cvref_t<decltype([&to_string = to_string, &sep](const auto &a, const auto &el) {
                return ((a + sep) + to_string(el));
                })>>)) && true)); return CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(v)).end()); }(), to_string([&]() -> decltype(auto) { static_assert(((!std::is_reference_v<decltype(ceto::bounds_check(v, 0))> ) && ceto::IsStateless<std::remove_cvref_t<decltype(to_string)>>)); return ceto::bounds_check(v, 0); }()), [&to_string = to_string, &sep](const auto &a, const auto &el) {
                return ((a + sep) + to_string(el));
                });
    }

    auto main() -> int {
        const auto l = [](const auto &a) {
                return std::to_string(a);
                };
        const auto csv = join(std::vector {{1, 2, 3, 4, 5}}, [&](const auto &a) {
                return l(a);
                }, ", ");
        const auto b = std::string {"blah"};
        const auto csv2 = join(std::vector {0}, [=](const auto &a) {
                return (b + std::to_string(a));
                });
        (std::cout << csv) << csv2;
    }

