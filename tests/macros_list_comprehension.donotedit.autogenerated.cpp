
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


#include <ranges>
;
#include "macros_list_comprehension.donotedit.autogenerated.h"
;
    auto main() -> int {
        const auto l = [&]() {
                auto ceto__private__ident__2 { std::vector<std::ranges::range_value_t<decltype(std::ranges::iota_view(0, 10))>>() } ;
                auto && ceto__private__ident__3 { std::ranges::iota_view(0, 10) } ;
                if constexpr (requires () {                std::size(ceto__private__ident__3);
}) {
                    (*ceto::mad(ceto__private__ident__2)).reserve(std::size(ceto__private__ident__3));
                }
                for(const auto& x : ceto__private__ident__3) {
                    if ((x % 2) == 0) {
                        (*ceto::mad(ceto__private__ident__2)).push_back(x);
                    }
                }
                if constexpr (!std::is_void_v<decltype(ceto__private__ident__2)>) { return ceto__private__ident__2; } else { static_cast<void>(ceto__private__ident__2); };
                }();
        for(const auto& x : l) {
            std::cout << x;
        }
        const auto l2 = [&]() {
                auto ceto__private__ident__0 { std::vector<decltype(std::declval<std::ranges::range_value_t<decltype([&]() {
                        auto ceto__private__ident__2 { std::vector<std::ranges::range_value_t<decltype(std::ranges::iota_view(0, 10))>>() } ;
                        auto && ceto__private__ident__3 { std::ranges::iota_view(0, 10) } ;
                        if constexpr (requires () {                        std::size(ceto__private__ident__3);
}) {
                            (*ceto::mad(ceto__private__ident__2)).reserve(std::size(ceto__private__ident__3));
                        }
                        for(const auto& x : ceto__private__ident__3) {
                            if ((x % 2) == 0) {
                                (*ceto::mad(ceto__private__ident__2)).push_back(x);
                            }
                        }
                        if constexpr (!std::is_void_v<decltype(ceto__private__ident__2)>) { return ceto__private__ident__2; } else { static_cast<void>(ceto__private__ident__2); };
                        }())>>()+1)>() } ;
                auto && ceto__private__ident__1 { l } ;
                if constexpr (requires () {                std::size(ceto__private__ident__1);
}) {
                    (*ceto::mad(ceto__private__ident__0)).reserve(std::size(ceto__private__ident__1));
                }
                for(const auto& x : ceto__private__ident__1) {
                    (*ceto::mad(ceto__private__ident__0)).push_back(x + 1);
                }
                if constexpr (!std::is_void_v<decltype(ceto__private__ident__0)>) { return ceto__private__ident__0; } else { static_cast<void>(ceto__private__ident__0); };
                }();
        for(const auto& i : [&]() {
                auto ceto__private__ident__4 { std::vector<std::ranges::range_value_t<decltype([&]() {
                        auto ceto__private__ident__0 { std::vector<decltype(std::declval<std::ranges::range_value_t<decltype([&]() {
                                auto ceto__private__ident__2 { std::vector<std::ranges::range_value_t<decltype(std::ranges::iota_view(0, 10))>>() } ;
                                auto && ceto__private__ident__3 { std::ranges::iota_view(0, 10) } ;
                                if constexpr (requires () {                                std::size(ceto__private__ident__3);
}) {
                                    (*ceto::mad(ceto__private__ident__2)).reserve(std::size(ceto__private__ident__3));
                                }
                                for(const auto& x : ceto__private__ident__3) {
                                    if ((x % 2) == 0) {
                                        (*ceto::mad(ceto__private__ident__2)).push_back(x);
                                    }
                                }
                                if constexpr (!std::is_void_v<decltype(ceto__private__ident__2)>) { return ceto__private__ident__2; } else { static_cast<void>(ceto__private__ident__2); };
                                }())>>()+1)>() } ;
                        auto && ceto__private__ident__1 { l } ;
                        if constexpr (requires () {                        std::size(ceto__private__ident__1);
}) {
                            (*ceto::mad(ceto__private__ident__0)).reserve(std::size(ceto__private__ident__1));
                        }
                        for(const auto& x : ceto__private__ident__1) {
                            (*ceto::mad(ceto__private__ident__0)).push_back(x + 1);
                        }
                        if constexpr (!std::is_void_v<decltype(ceto__private__ident__0)>) { return ceto__private__ident__0; } else { static_cast<void>(ceto__private__ident__0); };
                        }())>>() } ;
                auto && ceto__private__ident__5 { l2 } ;
                if constexpr (requires () {                std::size(ceto__private__ident__5);
}) {
                    (*ceto::mad(ceto__private__ident__4)).reserve(std::size(ceto__private__ident__5));
                }
                for(const auto& x : ceto__private__ident__5) {
                    if (x > 5) {
                        (*ceto::mad(ceto__private__ident__4)).push_back(x);
                    }
                }
                if constexpr (!std::is_void_v<decltype(ceto__private__ident__4)>) { return ceto__private__ident__4; } else { static_cast<void>(ceto__private__ident__4); };
                }()) {
            std::cout << i;
        }
        for(const auto& i : [&]() {
                auto ceto__private__ident__0 { std::vector<decltype(std::declval<std::ranges::range_value_t<decltype([&]() {
                        auto ceto__private__ident__2 { std::vector<std::ranges::range_value_t<decltype(std::ranges::iota_view(0, 10))>>() } ;
                        auto && ceto__private__ident__3 { std::ranges::iota_view(0, 10) } ;
                        if constexpr (requires () {                        std::size(ceto__private__ident__3);
}) {
                            (*ceto::mad(ceto__private__ident__2)).reserve(std::size(ceto__private__ident__3));
                        }
                        for(const auto& x : ceto__private__ident__3) {
                            if ((x % 2) == 0) {
                                (*ceto::mad(ceto__private__ident__2)).push_back(x);
                            }
                        }
                        if constexpr (!std::is_void_v<decltype(ceto__private__ident__2)>) { return ceto__private__ident__2; } else { static_cast<void>(ceto__private__ident__2); };
                        }())>>()*100)>() } ;
                auto && ceto__private__ident__1 { l } ;
                if constexpr (requires () {                std::size(ceto__private__ident__1);
}) {
                    (*ceto::mad(ceto__private__ident__0)).reserve(std::size(ceto__private__ident__1));
                }
                for(const auto& x : ceto__private__ident__1) {
                    (*ceto::mad(ceto__private__ident__0)).push_back(x * 100);
                }
                if constexpr (!std::is_void_v<decltype(ceto__private__ident__0)>) { return ceto__private__ident__0; } else { static_cast<void>(ceto__private__ident__0); };
                }()) {
            std::cout << i;
        }
    }

