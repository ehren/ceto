
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
        const auto x = [&]() {if (1) {
            return std::vector {{1, 2}};
        } else {
            return std::vector {{2, 1}};
        }}()
;
        std::cout << ceto::bounds_check(x, 0) << ceto::bounds_check(x, 1);
        std::cout << [&]() {if (1) {
            return 2;
        } else {
            return 1;
        }}()
;
    }

