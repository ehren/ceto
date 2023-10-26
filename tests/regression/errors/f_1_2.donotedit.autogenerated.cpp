
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

struct Point : ceto::shared_object {

    int a;

    int b;

    explicit Point(int a, int b) : a(a), b(b) {}

    Point() = delete;

};

    auto main() -> int {
        std::make_shared<const decltype(Point{1, 2})>(1, 2);
        const float x { 0 } ; static_assert(std::is_convertible_v<decltype(0), decltype(x)>);
        const float y { 0 } ; static_assert(std::is_convertible_v<decltype(0), decltype(y)>);
        std::make_shared<const decltype(Point{x, y})>(x, y);
    }

