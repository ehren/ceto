
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
//#include "ceto_private_boundscheck.donotedit.autogenerated.h"

#include "ceto_private_listcomp.donotedit.autogenerated.h"
;
#include "ceto_private_boundscheck.donotedit.autogenerated.h"
;
#include "ceto_private_convenience.donotedit.autogenerated.h"
;
#include <iostream>
;
    auto main() -> int {
        if constexpr (1) {
            const int x { 5 } ; static_assert(std::is_convertible_v<decltype(5), decltype(x)>);
            std::cout << x;
        }
        const float x { 5.0 } ; static_assert(std::is_convertible_v<decltype(5.0), decltype(x)>);
        std::cout << x;
    }

