#pragma once

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
#include <numeric>
;
#include <tuple>
;
#if defined(__clang__) && (__clang_major__ < 16)
        inline auto range(const size_t  start, const size_t  stop) -> std::vector<size_t> {
        auto r { std::vector<size_t>(stop - start) } ;
        std::iota((*ceto::mad(r)).begin(), (*ceto::mad(r)).end(), start);
        return r;
    }

        inline auto range(const size_t  stop) -> auto {
        return range(0u, stop);
    }

         template<typename Element> inline auto reversed( const std::vector<Element> &  container) -> auto {
        const auto rev = std::vector<Element>((*ceto::mad(container)).rbegin(), (*ceto::mad(container)).rend());
        return rev;
    }

#else
         template<typename ... Args> inline auto range( Args && ...  args) -> decltype(auto) {
        if constexpr (sizeof...(Args) == 1) {
            const typename std::tuple_element<0,std::tuple<Args...>> :: type zero { 0 } ; static_assert(std::is_convertible_v<decltype(0), decltype(zero)>);
            return std::ranges::iota_view(zero, std::forward<Args>(args)...);
        } else {
            return std::ranges::iota_view(std::forward<Args>(args)...);
        }
    }

         template<typename ... Args> inline auto reversed( Args && ...  args) -> decltype(auto) {
        return std::views::reverse(std::forward<Args>(args)...);
    }

#endif

