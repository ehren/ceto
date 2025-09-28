
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
constexpr const auto g = 1;
struct Foo : public ceto::shared_object, public std::enable_shared_from_this<Foo> {

    decltype(1) x = 1;

        inline auto foo() const -> void {
            const auto x = 2;
            std::cout << x;
        }

};

    auto main() -> int {
        const auto f = ceto::make_shared_propagate_const<const Foo>();
        (*ceto::mad(f)).foo();
    }

