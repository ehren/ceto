
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

;

;

;
#include "ceto_private_listcomp.donotedit.h"
;
#include "ceto_private_boundscheck.donotedit.h"
;
#include "ceto_private_convenience.donotedit.h"
;
#include "ceto_private_append_to_pushback.donotedit.h"
;
#include <iostream>
;
    auto main() -> int {
        const auto l { [](const auto &x) {
                return (x + 1);
                } } ;
        auto const l2 { [](const auto &x) -> int {
                return (x * 2);
                } } ;
        const auto l3 = [](const auto &x) {
                return (x * 3);
                };
        auto lmut { [](const auto &x) {
                return (x * 4);
                } } ;
        std::cout << l(2) << l2(2);
        std::cout << std::is_const_v<decltype(l)>;
        std::cout << std::is_const_v<decltype(l2)>;
        std::cout << std::is_const_v<decltype(l3)>;
        std::cout << !std::is_const_v<decltype(lmut)>;
    }

