
#include <string>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <sstream>
#include <functional>
#include <cassert>
#include <compare> // for <=>
#include <thread>
#include <optional>


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
#include "ceto_private_listcomp.donotedit.autogenerated.h"
;
#include "ceto_private_boundscheck.donotedit.autogenerated.h"
;
#include "ceto_private_convenience.donotedit.autogenerated.h"
;
#include "ceto_private_append_to_pushback.donotedit.autogenerated.h"
;
    auto main() -> int {
        const auto x = 5;
        auto l { std::vector {{1, 2, 3}} } ;
        
    
            static_assert(requires { std::begin(l) + 2; }, "not a contiguous container");
            size_t ceto__private__size2 = std::size(l);
            for (size_t ceto__private__idx1 = 0; ; ceto__private__idx1++) {
                if (std::size(l) != ceto__private__size2) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx1 >= ceto__private__size2) {
                    break;
                }
                 auto &&  x = l[ceto__private__idx1];
                            x = (x + 1);

            }
            
    
            static_assert(requires { std::begin(l) + 2; }, "not a contiguous container");
            size_t ceto__private__size4 = std::size(l);
            for (size_t ceto__private__idx3 = 0; ; ceto__private__idx3++) {
                if (std::size(l) != ceto__private__size4) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx3 >= ceto__private__size4) {
                    break;
                }
                const auto x = l[ceto__private__idx3];
                            if (1) {
                        // unsafe;
                        printf("%d", x);
                    }

            }
            
            auto&& ceto__private__intermediate5 = std::vector {{1, 2, 3}};

            static_assert(requires { std::begin(ceto__private__intermediate5) + 2; }, "not a contiguous container");
            size_t ceto__private__size7 = std::size(ceto__private__intermediate5);
            for (size_t ceto__private__idx6 = 0; ; ceto__private__idx6++) {
                if (std::size(ceto__private__intermediate5) != ceto__private__size7) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx6 >= ceto__private__size7) {
                    break;
                }
                 auto &&  x = ceto__private__intermediate5[ceto__private__idx6];
                            x = (x + 1);
                    if (1) {
                        // unsafe;
                        printf("%d", x);
                    }

            }
            if (1) {
            // unsafe;
            printf("%d", x);
        }
    }

