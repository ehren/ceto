
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
        struct Foo : public ceto::shared_object, public std::enable_shared_from_this<Foo> {

                        inline auto doit() const -> void {
                     // unsafe external C++: printf
;
                    printf("%d\n", 55 + 89);
                }

        };

        (*ceto::mad(ceto::make_shared_propagate_const<const Foo>())).doit();
    }

