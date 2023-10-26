
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

struct Foo : ceto::shared_object {

        inline auto operator+(const std::shared_ptr<const Foo>&  foo) const -> auto {
            const auto self = ceto::shared_from(this);
            printf("adding foo and foo (in the member function)\n");
            return self;
        }

        template <typename T1>
auto operator+(const T1& other) const -> auto {
            const auto self = ceto::shared_from(this);
            printf("adding foo and other (in the member function)\n");
            return self;
        }

};

    template <typename T2>
auto operator+(const std::shared_ptr<const Foo>&  f, const T2& x) -> auto {
        printf("adding foo and other\n");
        return ceto::mad(f)->operator+(x);
    }

    template <typename T1>
auto operator+(const T1& x, const std::shared_ptr<const Foo>&  f) -> auto {
        printf("adding other and foo\n");
        return ceto::mad(f)->operator+(x);
    }

    inline auto operator+(const std::shared_ptr<const Foo>&  x, const std::shared_ptr<const Foo>&  f) -> auto {
        printf("adding foo and foo\n");
        return ceto::mad(f)->operator+(x);
    }

    auto main() -> int {
        const auto n = 1;
        const auto k = 2;
        std::make_shared<const decltype(Foo())>() + 1;
        1 + std::make_shared<const decltype(Foo())>();
        std::make_shared<const decltype(Foo())>() + std::make_shared<const decltype(Foo())>();
    }

