
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
#include <ranges>
;
#include <iostream>
;

#define AUTO auto
;
    auto main() -> int {
        auto result { std::vector<std::ranges::range_value_t<std::remove_cvref_t<decltype(std::ranges::iota_view(0, 10))>>>() } ;
        auto && z { std::ranges::iota_view(0, 10) } ;
        
    
            static_assert(requires { std::begin(z) + 2; }, "not a contiguous container");
            size_t ceto__private__size2 = std::size(z);
            for (size_t ceto__private__idx1 = 0; ; ceto__private__idx1++) {
                if (std::size(z) != ceto__private__size2) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx1 >= ceto__private__size2) {
                    break;
                }
                const auto y = z[ceto__private__idx1];
                            (result).push_back([&]() -> decltype(auto) { static_assert(((!std::is_reference_v<decltype(y)> ) && true || ceto::IsContainer<std::remove_cvref_t<decltype(result)>>)); return y; }());

            }
            std::cout << (*ceto::mad(result)).size();
    }

