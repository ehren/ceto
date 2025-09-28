
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
        const auto x = 5;
        auto l { std::vector {{1, 2, 3}} } ;
        
for( auto rref  x : l) {
            x = (x + 1);
        }
        
    
            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(l)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size2 = std::size(l);
            for (size_t ceto__private__idx1 = 0; ; ceto__private__idx1++) {
                if (std::size(l) != ceto__private__size2) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx1 >= ceto__private__size2) {
                    break ;
                }
                const auto x = l[ceto__private__idx1];
                            /* unsafe: */ (printf("%d", x));

            }
            auto&& ceto__private__intermediate3 = std::vector {{1, 2, 3}};

for( auto rref  x : ceto__private__intermediate3) {
            x = (x + 1);
            if (1) {
// Unsafe
                printf("%d", x);
};
        }
        /* unsafe: */ (printf("%d", x));
    }

