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


#include <numeric>
;
#include <algorithm>
;
#include <cxxabi.h>
;

#if _MSC_VER
#define CETO_EXPORT __declspec(dllexport)
#else
#define CETO_EXPORT __attribute__((visibility("default")))
//#define CETO_EXPORT __attribute__((visibility("default"))) __attribute__((dll_export))
#endif
;
    template <typename T1, typename T2>
auto join(const T1& v, const T2& to_string, const decltype(std::string {""})&  sep = std::string {""}) -> auto {
if (ceto::mado(v)->empty()) {
            return std::string {""};
        }
        return std::accumulate(ceto::mado(v)->cbegin() + 1, ceto::mado(v)->cend(), to_string(ceto::maybe_bounds_check_access(v,0)), [&to_string, &sep](const auto &a, const auto &el) {
                if constexpr (!std::is_void_v<decltype(((a + sep) + to_string(el)))>) { return ((a + sep) + to_string(el)); } else { static_cast<void>(((a + sep) + to_string(el))); };
                });
    }

    inline auto string_replace(const std::string&  source, const std::string&  from, const std::string&  to) -> auto {
        auto new_string { std::string() } ;
        ceto::mado(new_string)->reserve(ceto::mado(source)->length());
        std::string::size_type last_pos { 0 } ; static_assert(std::is_convertible_v<decltype(0), decltype(last_pos)>);
        std::string::size_type find_pos { 0 } ; static_assert(std::is_convertible_v<decltype(0), decltype(find_pos)>);
while (std::string::npos != (find_pos = ceto::mado(source)->find(from, last_pos))) {            ceto::mado(new_string)->append(source, last_pos, find_pos - last_pos);
            new_string += to;
            last_pos = (find_pos + ceto::mado(from)->length());
        }
        ceto::mado(new_string)->append(source, last_pos, ceto::mado(source)->length() - last_pos);
        return new_string;
    }

    template <typename T1>
auto contains(const T1& container,  const typename std::remove_reference_t<decltype(container)> :: value_type &  element) -> auto {
        return (std::find(ceto::mado(container)->begin(), ceto::mado(container)->end(), element) != ceto::mado(container)->end());
    }

    template <typename T1>
auto typeid_name(const T1& object) -> auto {
        return abi::__cxa_demangle(ceto::mado(typeid(object))->name(), 0, 0, 0);
    }

