
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


    auto main() -> int {
        const auto x = [&]() {if (1) {
            return std::vector {{1, 2}};
        } else {
            return std::vector {{2, 1}};
        }}()
;
        (std::cout << ceto::maybe_bounds_check_access(x,0)) << ceto::maybe_bounds_check_access(x,1);
        const auto result = [](const auto &x) {
                if constexpr (!std::is_void_v<decltype([&]() {if (ceto::maybe_bounds_check_access(x,1) == 2) {
                    return ceto::maybe_bounds_check_access(x,1);
                } else {
                    return ceto::maybe_bounds_check_access(x,0);
                }}()
)>) { return [&]() {if (ceto::maybe_bounds_check_access(x,1) == 2) {
                    return ceto::maybe_bounds_check_access(x,1);
                } else {
                    return ceto::maybe_bounds_check_access(x,0);
                }}()
; } else { static_cast<void>([&]() {if (ceto::maybe_bounds_check_access(x,1) == 2) {
                    return ceto::maybe_bounds_check_access(x,1);
                } else {
                    return ceto::maybe_bounds_check_access(x,0);
                }}()
); };
                }(x);
        std::cout << [&]() {if (result) {
            return result;
        } else {
            return 0;
        }}()
;
        std::cout << [&]() {if (const auto r = [](const auto &x) {
                if constexpr (!std::is_void_v<decltype([&]() {if (ceto::maybe_bounds_check_access(x,1) == 2) {
                    return ceto::maybe_bounds_check_access(x,1);
                } else {
                    return ceto::maybe_bounds_check_access(x,0);
                }}()
)>) { return [&]() {if (ceto::maybe_bounds_check_access(x,1) == 2) {
                    return ceto::maybe_bounds_check_access(x,1);
                } else {
                    return ceto::maybe_bounds_check_access(x,0);
                }}()
; } else { static_cast<void>([&]() {if (ceto::maybe_bounds_check_access(x,1) == 2) {
                    return ceto::maybe_bounds_check_access(x,1);
                } else {
                    return ceto::maybe_bounds_check_access(x,0);
                }}()
); };
                }(x)) {
            return r;
        } else {
            return 0;
        }}()
;
        std::cout << [&]() {if (const auto r = [](const auto &x) {
                if constexpr (!std::is_void_v<decltype([&]() {if (ceto::maybe_bounds_check_access(x,1) == 2) {
                    return ceto::maybe_bounds_check_access(x,1);
                } else {
                    return ceto::maybe_bounds_check_access(x,0);
                }}()
)>) { return [&]() {if (ceto::maybe_bounds_check_access(x,1) == 2) {
                    return ceto::maybe_bounds_check_access(x,1);
                } else {
                    return ceto::maybe_bounds_check_access(x,0);
                }}()
; } else { static_cast<void>([&]() {if (ceto::maybe_bounds_check_access(x,1) == 2) {
                    return ceto::maybe_bounds_check_access(x,1);
                } else {
                    return ceto::maybe_bounds_check_access(x,0);
                }}()
); };
                }(x)) {
            return r;
        } else {
            return 0;
        }}()
;
        std::cout << [&]() {if (const auto r = [&]() {if (ceto::maybe_bounds_check_access(x,1) == 2) {
            return ceto::maybe_bounds_check_access(x,1);
        } else {
            return ceto::maybe_bounds_check_access(x,0);
        }}()
) {
            return r;
        } else {
            return 0;
        }}()
;
        std::cout << [&]() {if (const auto r = [&]() {if (ceto::maybe_bounds_check_access(x,1) == 2) {
            return ceto::maybe_bounds_check_access(x,1);
        } else {
            return ceto::maybe_bounds_check_access(x,0);
        }}()
) {
            return r;
        } else {
            return 0;
        }}()
;
        std::cout << [&]() {if ([&]() {if (ceto::maybe_bounds_check_access(x,1) == 2) {
            return ceto::maybe_bounds_check_access(x,1);
        } else {
            return ceto::maybe_bounds_check_access(x,0);
        }}()
) {
            return ceto::maybe_bounds_check_access(x,1);
        } else {
            return 0;
        }}()
;
        std::cout << [&]() {if ([&]() {if (ceto::maybe_bounds_check_access(x,1) == 2) {
            return ceto::maybe_bounds_check_access(x,1);
        } else {
            return ceto::maybe_bounds_check_access(x,0);
        }}()
) {
            return ceto::maybe_bounds_check_access(x,1);
        } else {
            return 0;
        }}()
;
    }

