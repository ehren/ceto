
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


// TODO these shouldn't be in all code - only for macro impls
#if _MSC_VER
#define CETO_EXPORT __declspec(dllexport)
#else
#define CETO_EXPORT __attribute__((visibility("default")))
#endif

#include <iostream>
;
;
auto main() -> int {
        const auto y = 10;
        std::cout << (((((-5) + y) + 1) + 2) + 3);
    }

