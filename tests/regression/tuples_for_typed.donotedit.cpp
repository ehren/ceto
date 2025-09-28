
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

#include <ranges>
;
    auto main() -> int {
        auto tuples { std::vector<decltype(std::make_tuple(std::declval<std::ranges::range_value_t<std::remove_cvref_t<decltype(std::ranges::iota_view(0, 10))>>>(), std::declval<std::ranges::range_value_t<std::remove_cvref_t<decltype(std::ranges::iota_view(0, 10))>>>()+1))>() } ;
        ceto::safe_for_loop<!std::is_reference_v<decltype(std::ranges::iota_view(0, 10))> && ceto::OwningContainer<std::remove_cvref_t<decltype(std::ranges::iota_view(0, 10))>>>(std::ranges::iota_view(0, 10), [&](auto &&ceto__private__lambda_param1) -> ceto::LoopControl {
    const auto i = ceto__private__lambda_param1;
            static_assert(std::is_same_v<decltype(i),const int>);
            (tuples).push_back(std::make_tuple(i, i + 1));
    return ceto::LoopControl::Continue;
});        
    
            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(tuples)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size3 = std::size(tuples);
            for (size_t ceto__private__idx2 = 0; ; ceto__private__idx2++) {
                if (std::size(tuples) != ceto__private__size3) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx2 >= ceto__private__size3) {
                    break ;
                }
                  const auto [x, y] = tuples[ceto__private__idx2];
                            std::cout << x << y << "\n";

            }
            
    
            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(tuples)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size5 = std::size(tuples);
            for (size_t ceto__private__idx4 = 0; ; ceto__private__idx4++) {
                if (std::size(tuples) != ceto__private__size5) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx4 >= ceto__private__size5) {
                    break ;
                }
                  auto & [x, y] = tuples[ceto__private__idx4];
                            static_assert(std::is_same_v<decltype((x)),int &>);
                    static_assert(std::is_same_v<decltype((y)),int &>);
                    if (1) {
        // Unsafe
                        x += 1;
                        y += 2;
        };

            }
            
    
            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(tuples)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size7 = std::size(tuples);
            for (size_t ceto__private__idx6 = 0; ; ceto__private__idx6++) {
                if (std::size(tuples) != ceto__private__size7) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx6 >= ceto__private__size7) {
                    break ;
                }
                  const auto [x, y] = tuples[ceto__private__idx6];
                            static_assert(std::is_same_v<decltype(x),const int>);
                    static_assert(std::is_same_v<decltype(y),const int>);
                    std::cout << x << y << "\n";

            }
            
    
            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(tuples)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size9 = std::size(tuples);
            for (size_t ceto__private__idx8 = 0; ; ceto__private__idx8++) {
                if (std::size(tuples) != ceto__private__size9) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx8 >= ceto__private__size9) {
                    break ;
                }
                  auto [x, y] = tuples[ceto__private__idx8];
                            static_assert(std::is_same_v<decltype(x),int>);
                    static_assert(std::is_same_v<decltype(y),int>);

            }
            
    
            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(tuples)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size11 = std::size(tuples);
            for (size_t ceto__private__idx10 = 0; ; ceto__private__idx10++) {
                if (std::size(tuples) != ceto__private__size11) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx10 >= ceto__private__size11) {
                    break ;
                }
                  const auto [x, y] = tuples[ceto__private__idx10];
                            static_assert(std::is_same_v<decltype(x),const int>);
                    static_assert(std::is_same_v<decltype(y),const int>);

            }
        }

