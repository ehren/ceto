
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


    auto main() -> int {
        const std::optional<std::string> x = "blah"; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype("blah"), std::remove_cvref_t<decltype(x)>>);
        std::optional<std::string> xm = "blah"; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype("blah"), std::remove_cvref_t<decltype(xm)>>);
        static_assert(std::is_same_v<decltype(x),const std::optional<std::string>>);
        static_assert(std::is_same_v<decltype(xm),std::optional<std::string>>);
        ((((std::cout << (*ceto::mad(x)).size()) << (*ceto::mad((*ceto::mad_smartptr(x)).value())).size()) << (*ceto::mad_smartptr(x)).value()) << (*ceto::mad(x)).c_str()) << (*ceto::mad((*ceto::mad_smartptr(x)).value())).c_str();
        ((((std::cout << (*ceto::mad(xm)).size()) << (*ceto::mad((*ceto::mad_smartptr(xm)).value())).size()) << (*ceto::mad_smartptr(xm)).value()) << (*ceto::mad(xm)).c_str()) << (*ceto::mad((*ceto::mad_smartptr(xm)).value())).c_str();
        xm = std::nullopt;
        std::cout << (*ceto::mad_smartptr(xm)).value_or("or");
    }

