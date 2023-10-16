
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

struct Uniq : ceto::object {

    std::remove_cvref_t<decltype(0)> x = 0;

        inline auto bar() -> auto {
            (this -> x) = ((this -> x) + 1);
            printf("in bar %d %p\n", this -> x, static_cast<const void *>(this));
            return (this -> x);
            (this -> x) = ((this -> x) + 1);
            printf("in bar %d %p\n", this -> x, static_cast<const void *>(this));
            return (this -> x);
        }

};

struct Shared : ceto::shared_object {

    std::remove_cvref_t<decltype(0)> x = 0;

        inline auto foo() const -> auto {
            printf("foo\n");
            return 10;
        }

};

    auto main() -> int {
        const auto x = 5;
        for( auto &&  x : std::vector {{1, 2, 3}}) {
            printf("%d\n", x);
            x = (x + 1);
        }
        static_assert(std::is_const_v<decltype(x)>);
        auto lst { std::vector {{1, 2, 3}} } ;
        for( auto &&  x : lst) {
            printf("%d\n", x);
            x = (x + 1);
        }
        for( auto &&  x : lst) {
            printf("%d\n", x);
            x = (x + 1);
        }
        auto u { std::vector<std::unique_ptr<decltype(Uniq{})>>() } ;
        auto s { std::vector<std::shared_ptr<const decltype(Shared{})>>() } ;
        for(const auto& x : std::vector {{1, 2, 3, 4, 5}}) {
            ceto::mad(u)->push_back(std::make_unique<decltype(Uniq())>());
            ceto::mad(s)->push_back(std::make_shared<const decltype(Shared())>());
        }
        for(const auto& x : u) {
            printf("%d\n", x -> bar());
            printf("%d\n", ceto::mado(x)->bar());
        }
        int n { 0 } ; static_assert(std::is_convertible_v<decltype(0), decltype(n)>);
        for(const auto& x : u) {
            printf("bar again: %d\n", ceto::mado(x)->bar());
            n = (n + 1);
if ((n % 2) == 0) {
                ceto::mado(x)->bar();
            }
        }
        for(const auto& x : u) {
            printf("bar again again: %d\n", ceto::mado(x)->bar());
        }
        auto v { std::vector {std::make_shared<decltype(Shared())>()} } ;
        auto v2 { std::vector {std::make_shared<const decltype(Shared())>()} } ;
        for(const auto& i : s) {
            ceto::mado(i)->foo();
            ceto::mad(v2)->push_back(i);
        }
        for(const auto& vv2 : v2) {
            ceto::mado(vv2)->foo();
        }
        const auto s1 = std::make_shared<decltype(Shared())>();
        for(const auto& v1 : v) {
            ceto::mado(v1)->x = 55;
            (std::cout << std::string {"v:"}) << ceto::mado(v1)->foo();
        }
    }

