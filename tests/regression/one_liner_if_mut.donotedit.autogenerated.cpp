
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

};

    auto main() -> int {
        if (std::make_shared<decltype(Foo())>()) {
            std::cout << 5;
        }
        if (std::make_shared<decltype(Foo())>()) {
            std::cout << 5;
        }
        if (std::make_shared<decltype(Foo())>()) {
            std::cout << 5;
        }
    }

