
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
        const int x { 0 } ; static_assert(std::is_convertible_v<decltype(0), decltype(x)>);
        int const & r2 = x; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(x), std::remove_cvref_t<decltype(r2)>>);
        const int & y = x; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(x), std::remove_cvref_t<decltype(y)>>);
    }

