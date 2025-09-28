
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
         int val;
         int val_east;
        if (1) {
// Unsafe
            int * const a = (&val); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype((&val)), std::remove_cvref_t<decltype(a)>>);
            int * const a2 = (&val_east); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype((&val_east)), std::remove_cvref_t<decltype(a2)>>);
            (*a) = 5;
            (*a2) = 5;
};
    }

