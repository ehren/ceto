
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
        const auto v = std::vector {{0, 1, 2}};
        (std :: cout) << CETO_UNSAFE_ARRAY_ACCESS([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(v)).data()))>  || (!std::is_reference_v<decltype(2)> && std::is_fundamental_v<std::remove_cvref_t<decltype(2)>>)) && true)  )); return CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(v)).data()); }(), 2);
    }

