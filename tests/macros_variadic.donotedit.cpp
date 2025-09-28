
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
#include <ranges>
;
#include <iostream>
;

;
    auto main() -> int {
        std::cout << (1 + 2 + 3);
        const auto c = "c";
        std::cout << (std::string {"a"} + "b" + c) << 5 << 0;
    }

