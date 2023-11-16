
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

    auto main() -> int {
 int x;
        x = 0;
        static_cast<void>(x);
        const auto f = []( const char *  y,  int  z) {
using namespace std;
typedef int t;
                const t w { 3 } ; static_assert(std::is_convertible_v<decltype(3), decltype(w)>);
                (((cout << y) << z) << w) << endl;
                z = 2;
                (cout << z) << endl;
                if constexpr (!std::is_void_v<decltype(void())>) { return void(); } else { static_cast<void>(void()); };
                };
        f("hi", 5);
    }

