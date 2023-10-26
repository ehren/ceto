
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
auto foo(const T1& bar) -> auto {
        return bar;
    }

    inline auto blah(const int  x) -> auto {
        return x;
    }

    auto main() -> int {
        const auto l = std::vector {{1, 2, 3}};
        printf("%d\n", ceto::maybe_bounds_check_access(l,0));
        const auto f = []() {
                if constexpr (!std::is_void_v<decltype(0)>) { return 0; } else { static_cast<void>(0); };
                };
        foo(f)();
        foo(printf);
        blah(1);
        printf;
    }

