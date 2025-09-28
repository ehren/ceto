
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

    int a;

    explicit Foo(const int  x) : a(x) {
    }

    Foo() = delete;

};

    auto main() -> int {
        std::cout << (*ceto::mad(ceto::make_shared_propagate_const<const Foo>(5))).a;
    }

