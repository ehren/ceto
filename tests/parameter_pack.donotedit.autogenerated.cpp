
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

    inline auto tprintf( const char *  format) -> void {
        std::cout << format;
    }

     template<typename T,typename ... Targs> inline auto tprintf( const char *  format, const T  value, const Targs ...  Fargs) -> void {
while ((*format) != ""[0]) {if ((*format) == "%"[0]) {
                std::cout << value;
                tprintf(format + 1, Fargs...);
                return;
            }
            std::cout << (*format);
            format = (format + 1);
        }
    }

    auto main() -> int {
        tprintf("% world% %\n", "Hello", "!"[0], 123);
    }

