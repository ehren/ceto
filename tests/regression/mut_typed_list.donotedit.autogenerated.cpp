
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


    inline auto byref(const std::vector<int>&  v) -> void {
        static_assert(std::is_reference_v<decltype(v)>);
        static_assert(std::is_const_v<std::remove_reference_t<decltype(v)>>);
        static_assert(std::is_same_v<decltype(v),const std::vector<int> &>);
    }

    inline auto byconstval( const std::vector<int>  v) -> void {
        static_assert(!std::is_reference_v<decltype(v)>);
        static_assert(std::is_const_v<std::remove_reference_t<decltype(v)>>);
        static_assert(std::is_same_v<decltype(v),const std::vector<int>>);
    }

    inline auto byref2( const std::vector<int> &  v) -> void {
        static_assert(std::is_reference_v<decltype(v)>);
        static_assert(std::is_const_v<std::remove_reference_t<decltype(v)>>);
        static_assert(std::is_same_v<decltype(v),const std::vector<int> &>);
    }

    inline auto byval( std::vector<int>  v) -> auto {
        static_assert(!std::is_reference_v<decltype(v)>);
        static_assert(!std::is_const_v<std::remove_reference_t<decltype(v)>>);
        static_assert(std::is_same_v<decltype(v),std::vector<int>>);
        ceto::mado(v)->push_back(5);
        return v;
    }

    inline auto byval4( std::vector<int>  v) -> auto {
        static_assert(!std::is_reference_v<decltype(v)>);
        static_assert(!std::is_const_v<std::remove_reference_t<decltype(v)>>);
        static_assert(std::is_same_v<decltype(v),std::vector<int>>);
        ceto::mado(v)->push_back(5);
        return v;
    }

    inline auto by_mut_ref( std::vector<int> &  v) -> auto {
        static_assert(std::is_reference_v<decltype(v)>);
        static_assert(!std::is_const_v<std::remove_reference_t<decltype(v)>>);
        static_assert(std::is_same_v<decltype(v),std::vector<int> &>);
        ceto::mado(v)->push_back(5);
        return v;
    }

    inline auto by_mut_ref2( std::vector<int> &  v) -> auto {
        static_assert(std::is_reference_v<decltype(v)>);
        static_assert(!std::is_const_v<std::remove_reference_t<decltype(v)>>);
        static_assert(std::is_same_v<decltype(v),std::vector<int> &>);
        ceto::mado(v)->push_back(5);
        return v;
    }

    auto main() -> int {
        std::vector<int> v = std::vector<int>{1, 2, 3}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<int>{1, 2, 3}), std::remove_cvref_t<decltype(v)>>);
        ceto::mad(v)->push_back(4);
        for(const auto& v : v) {
            std::cout << v;
        }
        byref(v);
        by_mut_ref(v);
        by_mut_ref2(v);
        for(const auto& v : byval(v)) {
            std::cout << v;
        }
    }

