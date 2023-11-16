
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

struct Blah : public ceto::shared_object, public std::enable_shared_from_this<Blah> {

        inline auto foo() const -> void {
            printf("in foo method\n");
        }

};

    auto main() -> int {
        const auto a = std::make_shared<const decltype(Blah())>();
        const auto b = std::make_shared<const decltype(Blah())>();
        const auto l = std::vector<std::shared_ptr<const Blah>>{a, b};
        ceto::mado(ceto::maybe_bounds_check_access(l,1))->foo();
        const auto s = std::vector<std::string>{"a", "b", "c"};
        printf("%s is the last element. %c is the first.\n", ceto::mado(ceto::maybe_bounds_check_access(s,2))->c_str(), ceto::maybe_bounds_check_access(ceto::maybe_bounds_check_access(s,0),0));
    }

