
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
struct Foo : public ceto::object {

    int x;

    explicit Foo(int x) : x(x) {}

    Foo() = delete;

};

    auto main() -> int {
        auto f = ceto::make_unique_nonullpropconst<const Foo>(2);
    }

