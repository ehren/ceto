
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
// unsafe;
    template <typename ceto__private__T11>
auto foo(const ceto__private__T11& bar) -> auto {
        return bar;
    }

    inline auto blah(const int  x) -> auto {
        return x;
    }

    auto main() -> int {
        const auto l = std::vector {{1, 2, 3}};
        printf("%d\n", ceto::bounds_check(l, 0));
        const auto f = []() {
                return 0;
                };
        foo(f)();
        foo(printf);
        blah(1);
        printf;
    }

