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
#if __clang_major__ < 16
        inline auto range(const size_t  start, const size_t  stop) -> std::vector<size_t> {
        auto r { std::vector<size_t>(stop - start) } ;
        std::iota(ceto::mado(r)->begin(), ceto::mado(r)->end(), start);
        return r;
    }

        inline auto range(const size_t  stop) -> auto {
        return range(0, stop);
    }

         template<typename Element> inline auto reversed(const std::vector<Element>  container) -> auto {
        const auto rev = std::vector<Element>(ceto::mado(container)->rbegin(), ceto::mado(container)->rend());
        return rev;
    }

#else
         template<typename ... Args> inline auto range( Args && ...  args) -> decltype(auto) {
        if constexpr (sizeof...(Args) == 1) {
            return std::ranges::iota_view(0, std::forward<Args>(args)...);
        } else {
            return std::ranges::iota_view(std::forward<Args>(args)...);
        }
    }

         template<typename ... Args> inline auto reversed( Args && ...  args) -> decltype(auto) {
        return std::views::reverse(std::forward<Args>(args)...);
    }

#endif

