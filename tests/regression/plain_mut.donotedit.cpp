
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
    inline auto foo(auto  x, decltype(10) y = 10) -> void {
        std::cout << x << y;
    }

    auto main() -> int {
        foo(1);
        auto&& ceto__private__intermediate1 = std::vector {{0, 1, 2}};

for(auto  x : ceto__private__intermediate1) {
            static_assert(std::is_same_v<decltype(x),int>);
        }
    }

