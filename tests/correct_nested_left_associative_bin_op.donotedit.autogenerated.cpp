
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
auto list_size(const T1& lst) -> void {
        (((std::cout << std::string {"list size: "}) << ceto::mado(lst)->size()) << std::string {" uh huh"}) << std::endl;
        printf("add: %d", ((1 + 2) + 3) + 4);
    }

    auto main() -> int {
        list_size(std::vector {{1, 2, 3, 4}});
    }

