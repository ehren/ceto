
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

    int x;

    int y;

    explicit Foo(const decltype(5)& x = 5, const decltype(4)& y = 4) : x(x), y(y) {
    }

};

    auto main() -> int {
        const auto f1 = ceto::make_shared_propagate_const<const Foo>();
        const auto f2 = ceto::make_shared_propagate_const<const Foo>(1);
        const auto f3 = ceto::make_shared_propagate_const<const Foo>(2, 3);
        auto&& ceto__private__intermediate1 = {f1, f2, f3};

for(const auto& f : ceto__private__intermediate1) {
            std::cout << (*ceto::mad(f)).x << (*ceto::mad(f)).y;
        }
    }

