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
namespace ceto {
    #if defined(CETO_HAS_SOURCE_LOCATION)
                inline auto bounds_check( auto &&  arr, const size_t  index,  const std::source_location & loc = std::source_location::current()) -> decltype(auto) requires (((requires () {        std::size(arr);
} && requires () {        CETO_UNSAFE_ARRAY_ACCESS(arr, index);
}) && requires () {        std::begin(arr) + 2;
})) {
            if (index >= std::size(arr)) {
                ((std::cerr << "terminating on out of bounds access: ") << (*ceto::mad(loc)).file_name()) << ":";
                (((((std::cerr << (*ceto::mad(loc)).function_name()) << ":") << (*ceto::mad(loc)).line()) << ":") << (*ceto::mad(loc)).column()) << "\n";
                std::terminate();
            }
            return CETO_UNSAFE_ARRAY_ACCESS(std::forward<decltype(arr)>(arr), std::forward<decltype(index)>(index));
        }

    #else
                inline auto bounds_check( auto &&  arr, const size_t  index) -> decltype(auto) requires (((requires () {        std::size(arr);
} && requires () {        CETO_UNSAFE_ARRAY_ACCESS(arr, index);
}) && requires () {        std::begin(arr) + 2;
})) {
            if (index >= std::size(arr)) {
                std::cerr << "terminating on out of bounds access\n";
                std::terminate();
            }
            return CETO_UNSAFE_ARRAY_ACCESS(std::forward<decltype(arr)>(arr), std::forward<decltype(index)>(index));
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
