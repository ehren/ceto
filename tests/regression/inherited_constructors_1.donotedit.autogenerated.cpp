
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


struct Base : public ceto::shared_object, public std::enable_shared_from_this<Base> {

    int a;

    explicit Base(int a) : a(a) {}

    Base() = delete;

};

struct Derived : public Base {

using Base::Base;

};

    auto main() -> int {
        const auto d = std::make_shared<const decltype(Derived{5})>(5);
        std::cout << (*ceto::mad(d)).a;
    }

