
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
        if constexpr (1) {
            const int x { 5 } ; static_assert(std::is_convertible_v<decltype(5), decltype(x)>);
            std::cout << x;
        }
        const float x { 5.0 } ; static_assert(std::is_convertible_v<decltype(5.0), decltype(x)>);
        std::cout << x;
    }

