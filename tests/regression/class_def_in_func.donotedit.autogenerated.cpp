
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
struct Foo : public ceto::shared_object, public std::enable_shared_from_this<Foo> {

                        inline auto doit() const -> void {
                    printf("%d\n", 55 + 89);
                }

        };

        ceto::mado(std::make_shared<const decltype(Foo())>())->doit();
    }

