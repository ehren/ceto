
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
    auto main() -> int {
        const auto [x, y] = std::make_tuple(0, 1);
        std::cout << x;
        std::cout << y;
        static_assert(std::is_same_v<decltype(x),const int>);
        static_assert(std::is_same_v<decltype(y),const int>);
    }

