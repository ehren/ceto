
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

//#include <concepts>
//#include <ranges>
//#include <numeric>


#include "ceto.h"

    inline auto f(const std::vector<std::vector<int>>&  a) -> void {
        std::cout << ceto::maybe_bounds_check_access(ceto::maybe_bounds_check_access(a,0),0);
    }

    inline auto f2(const std::vector<std::vector<int>>& a = std::vector<std::vector<int>>{std::vector {{0, 1}}}) -> void {
        std::cout << ceto::maybe_bounds_check_access(ceto::maybe_bounds_check_access(a,0),0);
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
                if constexpr (!std::is_void_v<decltype(f(a))>) { return f(a); } else { static_cast<void>(f(a)); };
                };
struct C : ceto::shared_object {

                    std::vector<std::vector<int>> a;

            explicit C(std::vector<std::vector<int>> a) : a(std::move(a)) {}

            C() = delete;

        };

        const auto c = std::make_shared<const decltype(C{l})>(l);
struct C2 : ceto::shared_object {

                    std::vector<std::vector<int>> a = std::vector<std::vector<int>>{std::vector {0}}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<std::vector<int>>{std::vector {0}}), std::remove_cvref_t<decltype(a)>>);

        };

        const auto c2 = std::make_shared<const decltype(C2())>();
        const auto ll = std::vector {{l, l2, l3, l4, l5, l6, l7, l9, ceto::mado(c)->a, ceto::mado(c2)->a}};
        const std::vector<std::vector<std::vector<int>>> ll2 = ll; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(ll), std::remove_cvref_t<decltype(ll2)>>);
        const auto ll3 = std::vector<std::vector<std::vector<int>>>{l, l2, l3};
        const std::vector<std::vector<std::vector<int>>> ll4 = std::vector<std::vector<std::vector<int>>>{l, l2, l3}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<std::vector<std::vector<int>>>{l, l2, l3}), std::remove_cvref_t<decltype(ll4)>>);
        const std::vector<std::vector<std::vector<int>>> ll5 = std::vector<std::vector<std::vector<int>>>{l, l2, l3}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<std::vector<std::vector<int>>>{l, l2, l3}), std::remove_cvref_t<decltype(ll5)>>);
        for(const auto& li : std::vector {{ll, ll2, ll3, ll4, ll5}}) {
            for(const auto& lk : li) {
                f(lk);
                f2(lk);
            }
        }
    }

