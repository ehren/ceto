
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
    inline auto blah(const int  x) -> auto {
        return x;
    }

    auto main() -> int {
        const auto l0 = [](const int  x) -> int {
                return 0;
                };
        const auto l = [](const int  x) -> int {
                return 0;
                }(0);
        const auto l2 = [](const int  x) -> decltype(0) {
                return 0;
                };
        const auto l3 = [](const int  x) -> decltype(1) {
                return 0;
                }(2);
        const auto l4 = [](const int  x) {
                return [x = ceto::default_capture(x)](const auto &y) {
                        return (y + x);
                        };
                };
        std::cout << l4(1)(2);
        const auto l5 = [](const int  x) {
                return [x = ceto::default_capture(x)](const auto &y) {
                        return (y + x);
                        };
                }(1)(1);
        std::cout << l5;
        
#if !defined(_MSC_VER)
            const auto l6 = [](const int  x) {
                    return [x = ceto::default_capture(x)](const auto &y) -> int {
                            return (y + x);
                            };
                    }(2)(3);
        
#else
            const auto l6 = [](const int  x) {
                    return [x = ceto::default_capture(x)](const auto &y) -> int {
                            return (y + x);
                            };
                    }(2)(3);
        
#endif

        std::cout << l6;
        
#if !defined(_MSC_VER)
            const auto l7 = [](const int  x) {
                    return [x = ceto::default_capture(x)](const auto &y) -> decltype(1) {
                            return (y + x);
                            };
                    }(3)(4);
        
#else
            const auto l7 = [](const int  x) {
                    return [x = ceto::default_capture(x)](const auto &y) -> decltype(1) {
                            return (y + x);
                            };
                    }(3)(4);
        
#endif

        std::cout << l7;
        static_assert(std::is_same_v<decltype(&blah),decltype(+[](const int  x) {
                return x;
                })>);
        static_assert(std::is_same_v<decltype(&blah),decltype(+[](const int  x) -> int {
                return x;
                })>);
        static_assert(std::is_same_v<decltype(&blah),decltype(+l0)>);
        static_assert(std::is_same_v<const int,decltype(l)>);
        static_assert(std::is_same_v<decltype(&blah),decltype(+l2)>);
        static_assert(std::is_same_v<const int,decltype(l3)>);
        const auto r = ([](const int  x) -> int {
                return (x + 1);
                }(0) + [](const int  x) -> int {
                return (x + 2);
                }(1));
        const auto r2 = ([](const int  x) {
                return (x + 1);
                }(0) + [](const int  x) {
                return (x + 2);
                }(1));
        std::cout << r << r2;
    }

