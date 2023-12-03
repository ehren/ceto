
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


struct A : ceto::object {
    virtual int foo(const std::shared_ptr<const A>&  x) const = 0;

    virtual int huh() const = 0;

    virtual ~A() = default;

};

struct Blah1 : public A, public ceto::shared_object, public std::enable_shared_from_this<Blah1> {

        auto foo(const std::shared_ptr<const A>&  x) const -> int {
            printf("Blah1 foo\n");
            return ceto::mado(x)->huh();
        }

        auto huh() const -> int {
            printf("huh 1\n");
            return 76;
        }

};

struct Blah2 : public A, public ceto::shared_object, public std::enable_shared_from_this<Blah2> {

        auto foo(const std::shared_ptr<const A>&  x) const -> int {
            printf("Blah2 foo\n");
            return ceto::mado(x)->huh();
        }

        auto huh() const -> int {
            printf("huh 2\n");
            return 89;
        }

};

    auto main() -> int {
        const auto a = std::make_shared<const decltype(Blah1())>();
        const auto b = std::make_shared<const decltype(Blah2())>();
        const auto l = std::vector<std::shared_ptr<const A>>{a, b};
        ceto::mado(ceto::maybe_bounds_check_access(l,0))->foo(ceto::maybe_bounds_check_access(l,1));
        ceto::mado(ceto::maybe_bounds_check_access(l,1))->foo(ceto::maybe_bounds_check_access(l,0));
    }

