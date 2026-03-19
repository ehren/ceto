
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
        const auto x = ((1) ?
            [&]() {
            return std::vector {{1, 2}};
        }() :
            [&]() {
            return std::vector {{2, 1}};
        }())
;
        std::cout << ceto::bounds_check(x, 0) << ceto::bounds_check(x, 1);
        const auto result = [](const auto &x) {
                return ((ceto::bounds_check(x, 1) == 2) ?
                    [&]() {
                    return ceto::bounds_check(x, 1);
                }() :
                    [&]() {
                    return ceto::bounds_check(x, 0);
                }())
;

                }(x);
        std::cout << ((result) ?
            [&]() {
            return result;
        }() :
            [&]() {
            return 0;
        }())
;
        std::cout << [&]() {
            const auto r = [](const auto &x) {
                return ((ceto::bounds_check(x, 1) == 2) ?
                    [&]() {
                    return ceto::bounds_check(x, 1);
                }() :
                    [&]() {
                    return ceto::bounds_check(x, 0);
                }())
;

                }(x);
            return (r) ?
                [&]() {
            return r;
        }() :
                [&]() {
            return 0;
        }();
        }()
;
        std::cout << [&]() {
            const auto r = [](const auto &x) {
                return ((ceto::bounds_check(x, 1) == 2) ?
                    [&]() {
                    return ceto::bounds_check(x, 1);
                }() :
                    [&]() {
                    return ceto::bounds_check(x, 0);
                }())
;

                }(x);
            return (r) ?
                [&]() {
            return r;
        }() :
                [&]() {
            return 0;
        }();
        }()
;
        std::cout << [&]() {
            const auto r = ((ceto::bounds_check(x, 1) == 2) ?
            [&]() {
            return ceto::bounds_check(x, 1);
        }() :
            [&]() {
            return ceto::bounds_check(x, 0);
        }());
            return (r) ?
                [&]() {
            return r;
        }() :
                [&]() {
            return 0;
        }();
        }()
;
        std::cout << [&]() {
            const auto r = ((ceto::bounds_check(x, 1) == 2) ?
            [&]() {
            return ceto::bounds_check(x, 1);
        }() :
            [&]() {
            return ceto::bounds_check(x, 0);
        }());
            return (r) ?
                [&]() {
            return r;
        }() :
                [&]() {
            return 0;
        }();
        }()
;
        std::cout << ((((ceto::bounds_check(x, 1) == 2) ?
            [&]() {
            return ceto::bounds_check(x, 1);
        }() :
            [&]() {
            return ceto::bounds_check(x, 0);
        }())) ?
            [&]() {
            return ceto::bounds_check(x, 1);
        }() :
            [&]() {
            return 0;
        }())
;
        std::cout << ((((ceto::bounds_check(x, 1) == 2) ?
            [&]() {
            return ceto::bounds_check(x, 1);
        }() :
            [&]() {
            return ceto::bounds_check(x, 0);
        }())) ?
            [&]() {
            return ceto::bounds_check(x, 1);
        }() :
            [&]() {
            return 0;
        }())
;
    }

