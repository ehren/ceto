
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
 // unsafe external C++: static_cast
;
    inline auto f(const std::vector<std::vector<int>>&  a) -> void {
        std::cout << ceto::bounds_check(ceto::bounds_check(a, 0), 0);
        static_assert(std::is_const_v<std::remove_reference_t<decltype(a)>>);
        static_assert(std::is_reference_v<decltype(a)>);
    }

    inline auto f2(const std::vector<std::vector<int>>& a = std::vector<std::vector<int>>{std::vector {{0, 1}}}) -> void {
        std::cout << ceto::bounds_check(ceto::bounds_check(a, 0), 0);
        std::cout << (*ceto::mad((*ceto::mad(a)).at(0))).at(0);
        const auto x = ceto::bounds_check(a, 0);
        std::cout << ceto::bounds_check(x, 0);
        static_assert(std::is_const_v<std::remove_reference_t<decltype(a)>>);
        static_assert(std::is_reference_v<decltype(a)>);
    }

    auto main() -> int {
        const auto l = std::vector {{std::vector {0}, std::vector {1}, std::vector {2}}};
        const std::vector<std::vector<int>> l2 = l; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(l), std::remove_cvref_t<decltype(l2)>>);
        const std::vector<std::vector<int>> l3 = std::vector {{std::vector {0}, std::vector {1}, std::vector {2}}}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector {{std::vector {0}, std::vector {1}, std::vector {2}}}), std::remove_cvref_t<decltype(l3)>>);
        const std::vector<std::vector<int>> l4 = l3; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(l3), std::remove_cvref_t<decltype(l4)>>);
        const std::vector<std::vector<int>> l5 = std::vector<std::vector<int>>{std::vector {0}, std::vector {1}}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<std::vector<int>>{std::vector {0}, std::vector {1}}), std::remove_cvref_t<decltype(l5)>>);
        const auto l6 = std::vector<std::vector<int>>{std::vector {0}, std::vector {1}};
        const std::vector<std::vector<int>> l7 = std::vector<std::vector<int>>{std::vector {0}, std::vector {1}}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<std::vector<int>>{std::vector {0}, std::vector {1}}), std::remove_cvref_t<decltype(l7)>>);
        const std::vector<std::remove_const_t<const std::vector<int>>> l9 = l7; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(l7), std::remove_cvref_t<decltype(l9)>>);
        const auto f2 = [](const std::vector<std::vector<int>>&  a) {
                static_assert(std::is_const_v<std::remove_reference_t<decltype(a)>>);
                static_assert(std::is_reference_v<decltype(a)>);
                return f(a);
                };
        struct C : public ceto::shared_object, public std::enable_shared_from_this<C> {

                    std::vector<std::vector<int>> a;

            explicit C(std::vector<std::vector<int>> a) : a(std::move(a)) {}

            C() = delete;

        };

        const auto c = ceto::make_shared_propagate_const<const C>(l);
        struct C2 : public ceto::shared_object, public std::enable_shared_from_this<C2> {

                    std::vector<std::vector<int>> a = std::vector<std::vector<int>>{std::vector {0}}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<std::vector<int>>{std::vector {0}}), std::remove_cvref_t<decltype(a)>>);

            decltype(std::vector {{std::vector {{1, 0}}}}) b = std::vector {{std::vector {{1, 0}}}};

        };

        const auto c2 = ceto::make_shared_propagate_const<const C2>();
        const auto ll = std::vector {{l, l2, l3, l4, l5, l6, l7, l9, (*ceto::mad(c)).a, (*ceto::mad(c2)).a}};
        const std::vector<std::vector<std::vector<int>>> ll2 = ll; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(ll), std::remove_cvref_t<decltype(ll2)>>);
        const auto ll3 = std::vector<std::vector<std::vector<int>>>{l, l2, l3};
        const std::vector<std::vector<std::vector<int>>> ll4 = std::vector<std::vector<std::vector<int>>>{l, l2, l3}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<std::vector<std::vector<int>>>{l, l2, l3}), std::remove_cvref_t<decltype(ll4)>>);
        const std::vector<std::vector<std::vector<int>>> ll5 = std::vector<std::vector<std::vector<int>>>{l, l2, l3}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<std::vector<std::vector<int>>>{l, l2, l3}), std::remove_cvref_t<decltype(ll5)>>);
        auto&& ceto__private__intermediate3 = std::vector {{ll, ll2, ll3, ll4, ll5}};

for(const auto& li : ceto__private__intermediate3) {
            
    
                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(li)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size2 = std::size(li);
                for (size_t ceto__private__idx1 = 0; ; ceto__private__idx1++) {
                    if (std::size(li) != ceto__private__size2) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx1 >= ceto__private__size2) {
                        break ;
                    }
                    const auto lk = li[ceto__private__idx1];
                                    f(lk);
                            f2(lk);

                }
            }
    }

