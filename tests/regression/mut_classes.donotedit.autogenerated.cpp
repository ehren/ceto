
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

template <typename _ceto_private_C1>struct Blah : public ceto::enable_shared_from_this_base_for_templates {

    _ceto_private_C1 x;

        inline auto foo() -> void {
            (this -> x) = ((this -> x) + 1);
        }

    explicit Blah(_ceto_private_C1 x) : x(std::move(x)) {}

    Blah() = delete;

};

    auto main() -> int {
        auto b { std::make_shared<decltype(Blah{1})>(1) } ;
        ceto::mado(b)->foo();
        std::cout << ceto::mado(b)->x;
        ceto::mado(b)->x = 5;
        std::cout << ceto::mado(b)->x;
    }

