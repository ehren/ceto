
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

        inline auto foo() const -> auto {
            printf("foo\n");
            return 5;
        }

};

    auto main() -> int {
        auto f { std::make_shared<decltype(Foo())>() } ;
        ceto::mado(f)->foo();
        auto f2 { f } ;
        ceto::mado(f2)->foo();
        (std::cout << (&f) -> use_count()) << std::endl;
        (std::cout << (&f2) -> use_count()) << std::endl;
        f2 = nullptr;
        f = nullptr;
        printf("f %d\n", !f);
        printf("f2 %d\n", !f2);
        (std::cout << (&f) -> use_count()) << std::endl;
        (std::cout << (&f2) -> use_count()) << std::endl;
        f -> foo();
        f2 -> foo();
    }

