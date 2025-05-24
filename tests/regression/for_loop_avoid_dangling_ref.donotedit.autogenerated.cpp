
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


#include "ceto.h"

struct Foo : public ceto::object {

    decltype(std::vector {{std::vector {{std::vector {{1, 2, 3}}, std::vector {1}}}, std::vector {{std::vector {2}}}, std::vector {{std::vector {{3, 4}}, std::vector {5}}}}}) a = std::vector {{std::vector {{std::vector {{1, 2, 3}}, std::vector {1}}}, std::vector {{std::vector {2}}}, std::vector {{std::vector {{3, 4}}, std::vector {5}}}}};

};

struct Bar : public ceto::object {

    decltype(Foo()) foo = Foo();

};

    auto main() -> int {
        const auto b = Bar();
        
            auto&& ceto__private__intermediate1 = (*ceto::mad(b)).foo;
        auto&& ceto__private__intermediate2 = (*ceto::mad(ceto__private__intermediate1)).a;
        auto&& ceto__private__intermediate3 = ceto::bounds_check(ceto__private__intermediate2,0);
        auto&& ceto__private__intermediate4 = ceto::bounds_check(ceto__private__intermediate3,0);
        auto&& ceto__private__intermediate5 = std::vector(ceto__private__intermediate4);

            static_assert(requires { std::begin(ceto__private__intermediate5) + 2; }, "not a contiguous container");
            size_t ceto__private__size7 = std::size(ceto__private__intermediate5);
            for (size_t ceto__private__idx6 = 0; ; ceto__private__idx6++) {
                if (std::size(ceto__private__intermediate5) != ceto__private__size7) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx6 >= ceto__private__size7) {
                    break;
                }
                const auto& i = ceto__private__intermediate5[ceto__private__idx6];
                            std::cout << i;

            }
        }

