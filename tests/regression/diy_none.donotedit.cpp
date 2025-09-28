
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
constexpr const auto None2 = nullptr;
constexpr auto const None3 { nullptr } ;
    auto main() -> int {
        std::cout << None2 << None3;
        static_assert(std::is_const_v<decltype(None2)>);
        static_assert(std::is_const_v<decltype(None3)>);
        static_assert(std::is_same_v<decltype(None2),const std::nullptr_t>);
    }

