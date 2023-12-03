
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

        inline auto huh() const -> void {
            (std::cout << "huh") << "\n";
        }

};

    auto main() -> int {
        ceto::mado(std::make_shared<const decltype(Blah())>())->huh();
        const auto b = std::make_shared<const decltype(Blah())>();
        ceto::mado(b)->huh();
        b -> huh();
        printf("addr %p\n", static_cast<const void *>((&b) -> get()));
        printf("use_count %ld\n", (&b) -> use_count());
        const auto b_addr = (&b);
        printf("addr of shared_ptr instance %p\n", static_cast<const void *>(b_addr));
        printf("addr %p\n", static_cast<const void *>(b_addr -> get()));
        printf("use_count %ld\n", b_addr -> use_count());
        ceto::mado((*b_addr))->huh();
        (*b_addr) -> huh();
    }

