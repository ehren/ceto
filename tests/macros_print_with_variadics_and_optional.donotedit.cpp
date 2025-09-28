
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

;

;
    auto main() -> int {
        const auto a = "a";
        std::cout << a << std::endl;
        std::cout << a << a << std::endl;
        std::cerr << "🙀" << a << a << std::endl;
        std::cerr << "🙀" << "b" << std::endl;
        std::cout << "b" << std::endl;
        std::cerr << "🙀" << std::endl;
        std::cout << std::endl;
    }

