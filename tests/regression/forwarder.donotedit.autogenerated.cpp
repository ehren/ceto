
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


     template<typename T,typename ... Args> inline auto forwarder( Args && ...  args) -> void {
        const T local = {std::forward<Args>(args)...};
    }

    auto main() -> int {
        forwarder<std::vector<int>>(1, 2, 3, 4);
    }

