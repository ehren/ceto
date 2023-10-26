
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

struct Base : ceto::shared_object {

};

struct Derived : public Base {

using Base::Base;

};

    auto main() -> int {
        const auto d = std::make_shared<const decltype(Derived())>();
    }

