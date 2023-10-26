
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

    int x { 0 } ; static_assert(std::is_convertible_v<decltype(0), decltype(x)>);

        inline auto bar() const -> void {
            printf("bar %d\n", this -> x);
        }

        ~Foo() {
            printf("dead\n");
        }

        inline auto operator==(const std::shared_ptr<const Foo>&  other) const -> auto {
            printf("in == method - both foo\n");
            return ((this -> x) == ceto::mado(other)->x);
        }

        template <typename T1>
auto operator==(const T1& other) const -> auto {
            printf("in == method - other not foo\n");
            return (other == 5);
        }

};

    template <typename T2>
auto operator==(const std::shared_ptr<const Foo>&  f, const T2& other) -> auto {
        return ceto::mad(f)->operator==(other);
    }

    inline auto operator==(const std::shared_ptr<const Foo>&  f, const std::shared_ptr<const Foo>&  otherfoo) -> auto {
        return ceto::mad(f)->operator==(otherfoo);
    }

    inline auto operator==(const std::shared_ptr<const Foo>&  f, const std::nullptr_t  other) -> auto {
        return !f;
    }

    auto main() -> int {
        const auto f = std::make_shared<const decltype(Foo())>();
        ceto::mado(f)->bar();
if (f == 5) {
            printf("overload == works\n");
        }
        const auto b = std::make_shared<const decltype(Foo())>();
if (f == b) {
            printf("same\n");
        } else {
            printf("not same\n");
        }
        const std::shared_ptr<const Foo> f2 = nullptr; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(nullptr), std::remove_cvref_t<decltype(f2)>>);
        printf("testing for null...\n");
if (f2 == nullptr) {
            printf("we're dead\n");
        }
if (!f2) {
            printf("we're dead\n");
        }
    }

