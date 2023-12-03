
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

    int a;

    explicit Foo(const int  x) : a(x) {
    }

    Foo() = delete;

};

    auto main() -> int {
        std::cout << ceto::mado(std::make_shared<const decltype(Foo{5})>(5))->a;
    }

