
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

struct Foo : public ceto::shared_object, public std::enable_shared_from_this<Foo> {

         static inline auto blah() -> void {
            std::cout << std::string {"blah"};
        }

};

    auto main() -> int {
        Foo :: blah();
        Foo::blah();
        (std::cout << ceto::mado(std :: vector(500, 5))->at(499)) << (std :: endl);
using std :: vector;
        const auto v = vector(500, 5);
        std::cout << ceto::mado(v)->at(499);
    }

