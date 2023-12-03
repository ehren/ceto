
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


    inline auto blah(const int  x) -> auto {
        return x;
    }

    auto main() -> int {
        const auto l0 = [](const int  x) -> int {
                if constexpr (!std::is_void_v<decltype(0)>&& !std::is_void_v<int>) { return 0; } else { static_cast<void>(0); };
                };
        const auto l = [](const int  x) -> int {
                if constexpr (!std::is_void_v<decltype(0)>&& !std::is_void_v<int>) { return 0; } else { static_cast<void>(0); };
                }(0);
        const auto l2 = [](const int  x) -> decltype(0) {
                if constexpr (!std::is_void_v<decltype(0)>&& !std::is_void_v<decltype(0)>) { return 0; } else { static_cast<void>(0); };
                };
        const auto l3 = [](const int  x) -> decltype(1) {
                if constexpr (!std::is_void_v<decltype(0)>&& !std::is_void_v<decltype(1)>) { return 0; } else { static_cast<void>(0); };
                }(2);
        const auto l4 = [](const int  x) {
                return [x = ceto::default_capture(x)](const auto &y) {
                        if constexpr (!std::is_void_v<decltype((y + x))>) { return (y + x); } else { static_cast<void>((y + x)); };
                        };
                };
        std::cout << l4(1)(2);
        const auto l5 = [](const int  x) {
                return [x = ceto::default_capture(x)](const auto &y) {
                        if constexpr (!std::is_void_v<decltype((y + x))>) { return (y + x); } else { static_cast<void>((y + x)); };
                        };
                }(1)(1);
        std::cout << l5;
        #if !defined(_MSC_VER)
            const auto l6 = [](const int  x) {
                    if constexpr (!std::is_void_v<decltype([x = ceto::default_capture(x)](const auto &y) -> int {
                            if constexpr (!std::is_void_v<decltype((y + x))>&& !std::is_void_v<int>) { return (y + x); } else { static_cast<void>((y + x)); };
                            })>) { return [x = ceto::default_capture(x)](const auto &y) -> int {
                            if constexpr (!std::is_void_v<decltype((y + x))>&& !std::is_void_v<int>) { return (y + x); } else { static_cast<void>((y + x)); };
                            }; } else { static_cast<void>([x = ceto::default_capture(x)](const auto &y) -> int {
                            if constexpr (!std::is_void_v<decltype((y + x))>&& !std::is_void_v<int>) { return (y + x); } else { static_cast<void>((y + x)); };
                            }); };
                    }(2)(3);
        #else
            const auto l6 = [](const int  x) {
                    return [x = ceto::default_capture(x)](const auto &y) -> int {
                            if constexpr (!std::is_void_v<decltype((y + x))>&& !std::is_void_v<int>) { return (y + x); } else { static_cast<void>((y + x)); };
                            };
                    }(2)(3);
        #endif

        std::cout << l6;
        #if !defined(_MSC_VER)
            const auto l7 = [](const int  x) {
                    if constexpr (!std::is_void_v<decltype([x = ceto::default_capture(x)](const auto &y) -> decltype(1) {
                            if constexpr (!std::is_void_v<decltype((y + x))>&& !std::is_void_v<decltype(1)>) { return (y + x); } else { static_cast<void>((y + x)); };
                            })>) { return [x = ceto::default_capture(x)](const auto &y) -> decltype(1) {
                            if constexpr (!std::is_void_v<decltype((y + x))>&& !std::is_void_v<decltype(1)>) { return (y + x); } else { static_cast<void>((y + x)); };
                            }; } else { static_cast<void>([x = ceto::default_capture(x)](const auto &y) -> decltype(1) {
                            if constexpr (!std::is_void_v<decltype((y + x))>&& !std::is_void_v<decltype(1)>) { return (y + x); } else { static_cast<void>((y + x)); };
                            }); };
                    }(3)(4);
        #else
            const auto l7 = [](const int  x) {
                    return [x = ceto::default_capture(x)](const auto &y) -> decltype(1) {
                            if constexpr (!std::is_void_v<decltype((y + x))>&& !std::is_void_v<decltype(1)>) { return (y + x); } else { static_cast<void>((y + x)); };
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
                if constexpr (!std::is_void_v<decltype((x + 1))>&& !std::is_void_v<int>) { return (x + 1); } else { static_cast<void>((x + 1)); };
                }(0) + [](const int  x) -> int {
                if constexpr (!std::is_void_v<decltype((x + 2))>&& !std::is_void_v<int>) { return (x + 2); } else { static_cast<void>((x + 2)); };
                }(1));
        const auto r2 = ([](const int  x) {
                if constexpr (!std::is_void_v<decltype((x + 1))>) { return (x + 1); } else { static_cast<void>((x + 1)); };
                }(0) + [](const int  x) {
                if constexpr (!std::is_void_v<decltype((x + 2))>) { return (x + 2); } else { static_cast<void>((x + 2)); };
                }(1));
        (std::cout << r) << r2;
    }

