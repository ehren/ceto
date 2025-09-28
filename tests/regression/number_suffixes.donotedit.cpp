
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
        const auto x = 10.0;
        const auto y = 10.00l;
        const auto z = 100ULL;
        const auto w = 10.0f;
        static_assert(std::is_same_v<decltype(x),const double>);
        static_assert(std::is_same_v<decltype(y),const long double>);
        static_assert(std::is_same_v<decltype(z),const unsigned long long>);
        static_assert(std::is_same_v<decltype(w),const float>);
    }

