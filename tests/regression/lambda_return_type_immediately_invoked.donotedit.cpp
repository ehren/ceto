
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
        const auto val = [](const auto &x) -> int {
                return x;
                }(5);
        std::cout << val;
        const auto val2 = [](const auto &x) -> const char ptr {
                return "hi";
                }(5);
        std::cout << val2;
    }

