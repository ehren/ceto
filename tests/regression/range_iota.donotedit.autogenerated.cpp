
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
#include <iostream>
;
     template<typename ... Args> inline auto range( Args && ...  args) -> decltype(auto) {
if constexpr (sizeof...(Args) == 1) {
            return std::ranges::iota_view(0, std::forward<Args>(args)...);
        } else {
            return std::ranges::iota_view(std::forward<Args>(args)...);
        }
    }

    auto main() -> int {
        for(const auto& i : range(10)) {
            std::cout << i;
        }
        for(const auto& i : range(0, 10)) {
            std::cout << i;
        }
        for(const auto& i : range((-10), 10)) {
            std::cout << i;
        }
    }

