
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

         static inline auto blah() -> void {
            std::cout << "blah";
        }

};

    auto main() -> int {
        Foo :: blah();
        Foo::blah();
        std::cout << (*ceto::mad(std :: vector(500, 5))).at(499) << (std :: endl);
        using std :: vector;
         // unsafe external C++: vector
;
        const auto v = vector(500, 5);
        std::cout << (*ceto::mad(v)).at(499);
    }

