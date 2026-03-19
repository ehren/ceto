
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
    inline auto is_void() -> void {
        ; // pass
    }

    auto main() -> int {
        const auto f = [](const auto &x) {
                std::cout << x << std::endl;
                return void();
                };
        f(1);
        static_assert(std::is_same_v<decltype(f(1)),void>);
        static_assert(std::is_same_v<decltype(is_void()),void>);
        const auto f2 = [](const auto &x) {
                return x;
                };
        std::cout << f2(2) << std::endl;
        static_assert(std::is_same_v<decltype(f2(2)),int>);
        const auto f3 = [](const auto &x) -> void {
                (std::cout << x << std::endl);
                };
        f3(3);
        static_assert(std::is_same_v<decltype(f3(3)),void>);
        const auto f4 = [](const auto &x) -> int {
                std::cout << x << std::endl;
                return x;
                };
        std::cout << f4(4) << std::endl;
        static_assert(std::is_same_v<decltype(f4(4)),int>);
        const auto val = [](const auto &x) -> int {
                return x;
                }(5);
        std::cout << val << std::endl;
    }

