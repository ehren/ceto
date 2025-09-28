
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
        auto x { std::vector<std::remove_cvref_t<decltype(ceto::bounds_check(std::declval<std::vector<decltype(1)>>(), 1))>>() } ;
        const auto zz = std::vector {{1, 2, 3}};
        (x).push_back([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(ceto::bounds_check(zz, 1))> ) && true)  || ceto::IsContainer<std::remove_cvref_t<decltype(x)>>)); return ceto::bounds_check(zz, 1); }());
        std::cout << ceto::bounds_check(x, 0);
    }

