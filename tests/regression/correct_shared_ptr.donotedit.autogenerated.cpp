
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

    std::remove_cvref_t<decltype(0)> x = 0;

        ~Foo() {
            printf("dead %p\n", static_cast<const void *>(this));
        }

        inline auto bar() const -> void {
            printf("in bar\n");
        }

        inline auto foo() const -> auto {
            const auto self = ceto::shared_from(this);
            printf("in foo method %p\n", static_cast<const void *>(this));
            bar();
            this -> bar();
            printf("bar attribute access %d\n", this -> x);
            printf("bar attribute access %d\n", x);
            return self;
        }

};

    template <typename T1>
auto calls_foo(const T1& x) -> auto {
        ceto::mado(x)->foo();
        return x;
    }

    auto main() -> int {
        ceto::mado(std::make_shared<const decltype(Foo())>())->foo();
        auto f { std::make_shared<decltype(Foo())>() } ;
        ceto::mado(f)->foo();
        ceto::mado(f)->x = 55;
        ceto::mado(f)->foo();
        const auto y = std::make_shared<const decltype(Foo())>();
        ceto::mado(ceto::mado(calls_foo(y))->foo())->foo();
    }

