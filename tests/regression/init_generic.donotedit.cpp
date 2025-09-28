
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
template <typename ceto__private__C1, typename ceto__private__C2>struct Generic : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C1 x;

    int y;

    ceto__private__C2 z;

    explicit Generic(ceto__private__C2 z, const ceto__private__C1 y) : x(y), y(99), z(z) {
    }

    Generic() = delete;

};

template <typename ceto__private__C3>struct GenericChild : public std::type_identity_t<decltype(Generic(std::declval<ceto__private__C3>(), std::vector {{1, 2, 3}}))> {

    explicit GenericChild(ceto__private__C3 x) : std::type_identity_t<decltype(Generic(std::declval<ceto__private__C3>(), std::vector {{1, 2, 3}}))> (x, std::vector {{1, 2, 3}}) {
    }

    GenericChild() = delete;

};

    auto main() -> int {
        const auto g = ceto::make_shared_propagate_const<const decltype(Generic{101, (-333)})>(101, (-333));
        const auto g2 = ceto::make_shared_propagate_const<const decltype(GenericChild{std::vector {{"x", "y", "z"}}})>(std::vector {{"x", "y", "z"}});
        std::cout << (*ceto::mad(g)).x << (*ceto::mad(g)).y << (*ceto::mad(g)).z;
        std::cout << ceto::bounds_check((*ceto::mad(g2)).x, 2) << (*ceto::mad(g2)).y << ceto::bounds_check((*ceto::mad(g2)).z, 1);
    }

