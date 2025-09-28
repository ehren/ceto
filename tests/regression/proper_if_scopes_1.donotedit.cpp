
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
        if (auto x { 5 } ) {
            x = 1;
        } else if (auto x { 2 } ) {
            x = 3;
        }
        const auto x = std::vector {{0, 1}};
    }

