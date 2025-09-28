
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
#include <algorithm>
;
    template <typename ceto__private__T11>
auto contains(const ceto__private__T11& container,  const typename std::remove_reference_t<decltype(container)> :: value_type &  element) -> auto {
         // unsafe external C++: std.find
;
        return (CETO_BAN_RAW_DEREFERENCABLE(std::find([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cbegin()))>  || (!std::is_reference_v<decltype([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cend()))>  || (!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cbegin()))> && std::is_fundamental_v<std::remove_cvref_t<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cbegin()))>> && !std::is_reference_v<decltype(element)> && std::is_fundamental_v<std::remove_cvref_t<decltype(element)>>)) && true)  )); return CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cend()); }())> && std::is_fundamental_v<std::remove_cvref_t<decltype([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cend()))>  || (!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cbegin()))> && std::is_fundamental_v<std::remove_cvref_t<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cbegin()))>> && !std::is_reference_v<decltype(element)> && std::is_fundamental_v<std::remove_cvref_t<decltype(element)>>)) && true)  )); return CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cend()); }())>> && !std::is_reference_v<decltype(element)> && std::is_fundamental_v<std::remove_cvref_t<decltype(element)>>)) && true)  )); return CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cbegin()); }(), [&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cend()))>  || (!std::is_reference_v<decltype([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cbegin()))>  || (!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cend()))> && std::is_fundamental_v<std::remove_cvref_t<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cend()))>> && !std::is_reference_v<decltype(element)> && std::is_fundamental_v<std::remove_cvref_t<decltype(element)>>)) && true)  )); return CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cbegin()); }())> && std::is_fundamental_v<std::remove_cvref_t<decltype([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cbegin()))>  || (!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cend()))> && std::is_fundamental_v<std::remove_cvref_t<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cend()))>> && !std::is_reference_v<decltype(element)> && std::is_fundamental_v<std::remove_cvref_t<decltype(element)>>)) && true)  )); return CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cbegin()); }())>> && !std::is_reference_v<decltype(element)> && std::is_fundamental_v<std::remove_cvref_t<decltype(element)>>)) && true)  )); return CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cend()); }(), element)) != CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(container)).cend()));
    }

     template<typename ... Args> inline auto range( Args && ...  args) -> decltype(auto) {
         // unsafe external C++: std.forward
;
        if constexpr (sizeof...(Args) == 1) {
            return std::ranges::iota_view(0, std::forward<Args>(args)...);
        } else {
            return std::ranges::iota_view(std::forward<Args>(args)...);
        }
    }

    auto main() -> int {
        const auto l = std::vector {{0, 1, 2, 10, 19, 20}};
        ceto::safe_for_loop<!std::is_reference_v<decltype(range(20))> && ceto::OwningContainer<std::remove_cvref_t<decltype(range(20))>>>(range(20), [&](auto &&ceto__private__lambda_param2) -> ceto::LoopControl {
    const auto i = ceto__private__lambda_param2;
            if (contains(l, [&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(i)>  || (!std::is_reference_v<decltype(l)> && std::is_fundamental_v<std::remove_cvref_t<decltype(l)>>)) && true)  )); return i; }())) {
                std::cout << i;
            }
    return ceto::LoopControl::Continue;
});    }

