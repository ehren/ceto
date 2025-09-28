
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
struct Foo : public ceto::shared_object, public std::enable_shared_from_this<Foo> {

};

    auto main() -> int {
        if (ceto::make_shared_propagate_const<Foo>()) {
            std::cout << 5;
        }
        if (ceto::make_shared_propagate_const<Foo>()) {
            std::cout << 5;
        }
        if (ceto::make_shared_propagate_const<Foo>()) {
            std::cout << 5;
        }
    }

