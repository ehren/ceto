
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
        auto v { std::vector<std::ranges::range_value_t<std::vector<decltype(0)>>>() } ;
        auto v2 { std::vector<std::ranges::range_value_t<std::vector<std::ranges::range_value_t<std::vector<decltype(0)>>>>>() } ;
        const auto range = std::vector {{0, 1, 2}};
        
for(const auto& x : range) {
            (v).push_back([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(x)> ) && true)  || ceto::IsContainer<std::remove_cvref_t<decltype(v)>>)); return x; }());
        }
        auto&& ceto__private__intermediate1 = std::vector {{0, 1, 2}};

for(const auto& x : ceto__private__intermediate1) {
            (v).push_back([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(x)> ) && true)  || ceto::IsContainer<std::remove_cvref_t<decltype(v)>>)); return x; }());
        }
        
    
            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(v)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size3 = std::size(v);
            for (size_t ceto__private__idx2 = 0; ; ceto__private__idx2++) {
                if (std::size(v) != ceto__private__size3) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx2 >= ceto__private__size3) {
                    break ;
                }
                const auto x = v[ceto__private__idx2];
                            (v2).push_back([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(x)> ) && true)  || ceto::IsContainer<std::remove_cvref_t<decltype(v2)>>)); return x; }());
                    (v2).push_back([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(x)> ) && true)  || ceto::IsContainer<std::remove_cvref_t<decltype(v2)>>)); return x; }());

            }
            
    
            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(v2)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size5 = std::size(v2);
            for (size_t ceto__private__idx4 = 0; ; ceto__private__idx4++) {
                if (std::size(v2) != ceto__private__size5) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx4 >= ceto__private__size5) {
                    break ;
                }
                const auto x = v2[ceto__private__idx4];
                            std::cout << x;

            }
        }

