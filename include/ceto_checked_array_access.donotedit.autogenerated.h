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
#include <map>
;
    inline auto ceto_bounds_check( auto &&  arr,  size_t  index) -> decltype(auto) requires (requires () {    std::size(arr);
}) {
        if (index >= std::size(arr)) {
            std::cerr << "terminating on out of bounds access";
            std::terminate();
        }
        return std::forward<decltype(arr)>(arr)[std::forward<decltype(index)>(index)];
    }

    inline auto ceto_bounds_check( auto &&  o,  auto &&  index) -> decltype(auto) requires (!std::is_integral_v<std::remove_cvref_t<decltype(index)>>) {
        return std::forward<decltype(o)>(o)[std::forward<decltype(index)>(index)];
    }

template<class T> concept ceto_is_map_type = std::same_as<typename T::value_type,std::pair<const typename T::key_type,typename T::mapped_type>>;
    inline auto ceto_bounds_check( auto &&  m,  auto &&  key) -> decltype(auto) requires ((std::is_integral_v<std::remove_cvref_t<decltype(key)>> && ceto_is_map_type<std::remove_cvref_t<decltype(m)>>)) {
        return std::forward<decltype(m)>(m)[std::forward<decltype(key)>(key)];
    }

