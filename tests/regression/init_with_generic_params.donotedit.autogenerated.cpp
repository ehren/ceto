
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


template <typename ceto__private__C1>struct Foo : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C1 x;

    explicit Foo(ceto__private__C1 p) : x(std::move(p)) {
    }

    Foo() = delete;

};

    auto main() -> int {
        std::cout << ceto::mado(std::make_shared<const decltype(Foo{5})>(5))->x;
    }

