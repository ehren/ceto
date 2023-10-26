
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

struct Foo : ceto::shared_object {

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

