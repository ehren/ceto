
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

    template <typename T1>
auto contains(const T1& container,  const typename std::remove_reference_t<decltype(container)> :: value_type &  element) -> auto {
        return (std::find(ceto::mado(container)->begin(), ceto::mado(container)->end(), element) != ceto::mado(container)->end());
    }

    auto main() -> int {
        const auto l = std::vector {{0, 1, 2, 10, 19, 20}};
        static_assert(std::is_same_v<std::remove_cvref_t<decltype(0)>, std::remove_cvref_t<decltype(20)>>);
        for (std::remove_cvref_t<decltype(0)> i = 0; i < 20; ++i) {
if (contains(l, i)) {
                std::cout << i;
            }
        }
    }

