
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
template <typename ceto__private__C1>struct Foo : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C1 x;

    explicit Foo(ceto__private__C1 p) : x(p) {
    }

    Foo() = delete;

};

    auto main() -> int {
        std::cout << (*ceto::mad(ceto::make_shared_propagate_const<const decltype(Foo{5})>(5))).x;
    }

