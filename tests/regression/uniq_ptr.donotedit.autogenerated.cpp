
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


struct Foo : public ceto::object {

    int a { 5 } ; static_assert(std::is_convertible_v<decltype(5), decltype(a)>);

        inline auto bar() const -> auto {
            printf("bar %d\n", this -> a);
            return (this -> a);
        }

};

    inline auto bam( std::unique_ptr<const Foo>  f) -> void {
        ceto::mado(f)->bar();
    }

    inline auto baz( std::unique_ptr<const Foo>  f) -> void {
        ceto::mado(f)->bar();
        bam(std::move(f));
    }

    auto main() -> int {
        ceto::mado(std::make_unique<const decltype(Foo())>())->bar();
        baz(std::make_unique<const decltype(Foo())>());
        auto f = std::make_unique<decltype(Foo())>();
        ceto::mado(f)->bar();
        auto f2 = std::make_unique<decltype(Foo())>();
        ceto::mado(f2)->bar();
        baz(std::move(f2));
        auto lst { std::vector<std::unique_ptr<decltype(Foo())>>() } ;
        ceto::mad(lst)->push_back(std::make_unique<decltype(Foo())>());
        f = std::make_unique<decltype(Foo())>();
        ceto::mad(lst)->push_back(std::move(f));
        ceto::mado(ceto::maybe_bounds_check_access(lst,0))->bar();
        ceto::mado(ceto::maybe_bounds_check_access(lst,1))->bar();
    }

