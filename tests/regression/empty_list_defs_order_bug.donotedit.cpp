
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

#define AUTO auto
;
    auto main() -> int {
        auto result { std::vector<std::ranges::range_value_t<std::remove_cvref_t<decltype(std::ranges::iota_view(0, 10))>>>() } ;
        auto z { std::ranges::iota_view(0, 10) } ;
        ceto::safe_for_loop<!std::is_reference_v<decltype(z)> && ceto::OwningContainer<std::remove_cvref_t<decltype(z)>>>(z, [&](auto &&ceto__private__lambda_param1) -> ceto::LoopControl {
    const auto y = ceto__private__lambda_param1;
            (result).push_back([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(y)> ) && true)  || ceto::IsContainer<std::remove_cvref_t<decltype(result)>>)); return y; }());
    return ceto::LoopControl::Continue;
});        std::cout << (*ceto::mad(result)).size();
    }

