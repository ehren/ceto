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


#include "ceto.h"

#include <iostream>
;
// unsafe;

#define CETO_UNSAFE_ARRAY_ACCESS(array, index) (array[index])
;

;

;

;
namespace ceto {
    namespace util {
                inline auto maybe_signed_size( auto &&  arg) -> auto {
            if constexpr (std::is_signed_v<std::remove_cvref_t<decltype(arg)>>) {
                return std::ssize(arg);
            } else {
                return std::size(arg);
            }
        }


};
    #if defined(CETO_HAS_SOURCE_LOCATION)
                inline auto bounds_check( auto &&  arr,  auto &&  index,  const std::source_location & loc = std::source_location::current()) -> decltype(auto) requires ((std::is_integral_v<std::remove_cvref_t<decltype(index)>> && requires () {        std::size(arr);
        std::ssize(arr);
        CETO_UNSAFE_ARRAY_ACCESS(arr, index);
        std::begin(arr) + 2;
})) {
            if (!((0 <= index) && (index < util::maybe_signed_size(arr)))) {
                ((((std::cerr << "terminating on out of bounds access. index: ") << index) << " size: ") << util::maybe_signed_size(arr)) << ". ";
                (((((((std::cerr << (*ceto::mad(loc)).file_name()) << ":") << (*ceto::mad(loc)).function_name()) << ":") << (*ceto::mad(loc)).line()) << ":") << (*ceto::mad(loc)).column()) << "\n";
                std::terminate();
            }
            if constexpr (std::is_integral_v<std::remove_cvref_t<decltype(arr)>>) {
                return CETO_UNSAFE_ARRAY_ACCESS(std::forward<decltype(arr)>(arr), std::forward<decltype(index)>(index));
            } else {
                return CETO_UNSAFE_ARRAY_ACCESS(std::forward<decltype(arr)>(arr), static_cast<std::size_t>(std::forward<decltype(index)>(index)));
            }
        }

    #else
                inline auto bounds_check( auto &&  arr,  auto &&  index) -> decltype(auto) requires ((std::is_integral_v<std::remove_cvref_t<decltype(index)>> && requires () {        std::size(arr);
        std::ssize(arr);
        CETO_UNSAFE_ARRAY_ACCESS(arr, index);
        std::begin(arr) + 2;
})) {
            if (!((0 <= index) && (index < util::maybe_signed_size(arr)))) {
                ((((std::cerr << "terminating on out of bounds access. index: ") << index) << " size: ") << util::maybe_signed_size(arr)) << ". ";
                (((((((std::cerr << std::string {"(file_name() unavailable - no std.source_location)"}) << ":") << std::string {"(function_name() unavailable)"}) << ":") << 0) << ":") << 0) << "\n";
                std::terminate();
            }
            if constexpr (std::is_integral_v<std::remove_cvref_t<decltype(arr)>>) {
                return CETO_UNSAFE_ARRAY_ACCESS(std::forward<decltype(arr)>(arr), std::forward<decltype(index)>(index));
            } else {
                return CETO_UNSAFE_ARRAY_ACCESS(std::forward<decltype(arr)>(arr), static_cast<std::size_t>(std::forward<decltype(index)>(index)));
            }
        }

    #endif

        inline auto bounds_check( auto &&  non_array,  auto &&  obj) -> decltype(auto) requires (!std::is_integral_v<std::remove_cvref_t<decltype(obj)>>) {
        return CETO_UNSAFE_ARRAY_ACCESS(std::forward<decltype(non_array)>(non_array), std::forward<decltype(obj)>(obj));
    }

    template<class T> concept is_map_type = std::same_as<typename T::value_type,std::pair<const typename T::key_type,typename T::mapped_type>>;
        inline auto bounds_check( auto &&  map_like,  auto &&  key) -> decltype(auto) requires ((std::is_integral_v<std::remove_cvref_t<decltype(key)>> && is_map_type<std::remove_cvref_t<decltype(map_like)>>)) {
        return CETO_UNSAFE_ARRAY_ACCESS(std::forward<decltype(map_like)>(map_like), std::forward<decltype(key)>(key));
    }


};
