
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


    template <typename T1>
auto moretest2(const T1& p) -> void {
        (std::cout << p) << "\n";
        const auto l = std::vector {{1, 2, 3}};
        const std::vector<int> a = l; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(l), std::remove_cvref_t<decltype(a)>>);
        const auto b = std::vector {{1, 2, 3, 4}};
    }

    inline auto moretest( int const * const * const *  p) -> void {
        (std::cout << p) << "\n";
    }

    inline auto test( int const *  p) -> void {
        (std::cout << p) << "\n";
    }

    inline auto test( int * const  p) -> void {
        (std::cout << p) << "\n";
    }

    inline auto test2( int const * const  p) -> void {
        (std::cout << p) << "\n";
    }

    inline auto test( int * const *  p) -> void {
        (std::cout << p) << "\n";
    }

    inline auto test3( const int * const  p) -> void {
        (std::cout << p) << "\n";
    }

    inline auto bar( int const &  x) -> void {
        printf("int by const ref %d", x);
    }

    inline auto foo(const std::vector<std::string>&  items) -> void {
        ((std::cout << "size: ") << ceto::mado(items)->size()) << "\n";
        for(const auto& s : items) {
            (std::cout << s) << "\n";
        }
    }

    auto main(const int  argc, const char * *  argv) -> int {
        printf("argc %d\n", argc);
        assert(ceto::mado(std::string(argv[0]))->length() > 0);
        const auto lst = std::vector {{std::string {"hello"}, std::string {"world"}}};
        foo(lst);
        bar(ceto::mado(lst)->size());
    }

