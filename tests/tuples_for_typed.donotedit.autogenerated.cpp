
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


#include <ranges>
;
    auto main() -> int {
        auto tuples { std::vector<decltype(std::make_tuple(std::declval<std::ranges::range_value_t<decltype(std::ranges::iota_view(0, 10))>>(), std::declval<std::ranges::range_value_t<decltype(std::ranges::iota_view(0, 10))>>()+1))>() } ;
        for(const auto& i : std::ranges::iota_view(0, 10)) {
            static_assert(std::is_same_v<decltype(i),const int &>);
            ceto::mad(tuples)->push_back(std::make_tuple(i, i + 1));
        }
        for(  const auto& [x, y] : tuples) {
            ((std::cout << x) << y) << std::string {"\n"};
        }
        for(  auto & [x, y] : tuples) {
            static_assert(std::is_same_v<decltype((x)),int &>);
            static_assert(std::is_same_v<decltype((y)),int &>);
            x += 1;
            y += 2;
        }
        for(  const auto& [x, y] : tuples) {
            static_assert(std::is_same_v<decltype((x)),const int &>);
            static_assert(std::is_same_v<decltype((y)),const int &>);
            ((std::cout << x) << y) << std::string {"\n"};
        }
        for(  auto [x, y] : tuples) {
            static_assert(std::is_same_v<decltype(x),int>);
            static_assert(std::is_same_v<decltype(y),int>);
        }
        for(  const auto [x, y] : tuples) {
            static_assert(std::is_same_v<decltype(x),const int>);
            static_assert(std::is_same_v<decltype(y),const int>);
        }
    }

