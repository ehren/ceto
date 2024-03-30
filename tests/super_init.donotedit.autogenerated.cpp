
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


template <typename ceto__private__C1>struct Generic : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C1 x;

    explicit Generic(ceto__private__C1 x) : x(std::move(x)) {}

    Generic() = delete;

};

struct Concrete : public std::type_identity_t<decltype(Generic(std::declval<const int>()))> {

    explicit Concrete(const int  x) : std::type_identity_t<decltype(Generic(std::declval<const int>()))> (std::move(x)) {
    }

    Concrete() = delete;

};

template <typename ceto__private__C2, typename ceto__private__C3>struct Generic2 : public std::type_identity_t<decltype(Generic(std::declval<ceto__private__C3>()))> {

    ceto__private__C2 y;

    explicit Generic2(ceto__private__C3 x, ceto__private__C2 y) : std::type_identity_t<decltype(Generic(std::declval<ceto__private__C3>()))> (std::move(x)), y(std::move(y)) {
    }

    Generic2() = delete;

};

    auto main() -> int {
        const auto f = std::make_shared<const decltype(Generic{5})>(5);
        const auto f2 = std::make_shared<const decltype(Generic{"5"})>("5");
        const auto f3 = std::make_shared<const decltype(Generic2{std::vector {5}, "5"})>(std::vector {5}, "5");
        ((std::cout << (*ceto::mad(f)).x) << (*ceto::mad(f2)).x) << ceto::maybe_bounds_check_access((*ceto::mad(f3)).x,0);
    }

