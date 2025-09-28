
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
#include <array>
;
    auto main() -> int {
        const auto a = std::array<int,3>{1, 2, 3};
        const std::array<int,3> a3 = {1, 2, 3};
        const std::array<int,3> a4 = std::array<int,3>{1, 2, 3}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::array<int,3>{1, 2, 3}), std::remove_cvref_t<decltype(a4)>>);
        const auto v = std::vector<int>{1, 2};
        const auto v2 = std::vector<int>(30, 5);
        const std::vector<int> v3 = {30, 5};
        auto&& ceto__private__intermediate3 = {a, a3, a4};

for(const auto& x : ceto__private__intermediate3) {
            
    
                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(x)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size2 = std::size(x);
                for (size_t ceto__private__idx1 = 0; ; ceto__private__idx1++) {
                    if (std::size(x) != ceto__private__size2) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx1 >= ceto__private__size2) {
                        break ;
                    }
                    const auto i = x[ceto__private__idx1];
                                    std::cout << i;

                }
            }
        auto&& ceto__private__intermediate6 = {v, v2, v3};

for(const auto& x : ceto__private__intermediate6) {
            
    
                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(x)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size5 = std::size(x);
                for (size_t ceto__private__idx4 = 0; ; ceto__private__idx4++) {
                    if (std::size(x) != ceto__private__size5) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx4 >= ceto__private__size5) {
                        break ;
                    }
                    const auto i = x[ceto__private__idx4];
                                    std::cout << i;

                }
            }
        ceto::safe_for_loop<!std::is_reference_v<decltype(std::array{a, a3, a4})> && ceto::OwningContainer<std::remove_cvref_t<decltype(std::array{a, a3, a4})>>>(std::array{a, a3, a4}, [&](auto &&ceto__private__lambda_param9) -> ceto::LoopControl {
    const auto x = ceto__private__lambda_param9;
            
    
                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(x)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size8 = std::size(x);
                for (size_t ceto__private__idx7 = 0; ; ceto__private__idx7++) {
                    if (std::size(x) != ceto__private__size8) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx7 >= ceto__private__size8) {
                        break ;
                    }
                    const auto i = x[ceto__private__idx7];
                                    std::cout << i;

                }
    
    return ceto::LoopControl::Continue;
});        const auto get = [](const auto &t) -> void {
                (std::cout << ceto::bounds_check(std::get<0>(t), 0));
                };
        const auto t = std::tuple{a, a3, a4, v, v2, v3};
        const auto t2 = std::make_tuple(a, v);
        get(t);
        get(t2);
    }

