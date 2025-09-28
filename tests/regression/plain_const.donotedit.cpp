
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
constexpr const auto g { 5 } ; static_assert(std::is_convertible_v<decltype(5), decltype(g)>);
    auto main() -> int {
        const auto c { 2 } ; static_assert(std::is_convertible_v<decltype(2), decltype(c)>);
        static_assert(std::is_const_v<decltype(c)>);
        static_assert(std::is_const_v<decltype(g)>);
        std::cout << c << g;
    }

