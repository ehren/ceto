
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
    template <typename T1>
auto contains(const T1& container,  const typename std::remove_reference_t<decltype(container)> :: value_type &  element) -> auto {
        return (std::find(ceto::mado(container)->begin(), ceto::mado(container)->end(), element) != ceto::mado(container)->end());
    }

     template<typename ... Args> inline auto range( Args && ...  args) -> decltype(auto) {
if constexpr (sizeof...(Args) == 1) {
            return std::ranges::iota_view(0, std::forward<Args>(args)...);
        } else {
            return std::ranges::iota_view(std::forward<Args>(args)...);
        }
    }

    auto main() -> int {
        const auto l = std::vector {{0, 1, 2, 10, 19, 20}};
        for(const auto& i : range(20)) {
if (contains(l, i)) {
                std::cout << i;
            }
        }
    }

