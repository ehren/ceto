
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
        auto y { 1 } ;
        const auto x = (y = 0);
        std::cout << x << y;
        const auto y2 = (y = x);
        static_assert(std::is_same_v<decltype(y2),const int>);
    }

