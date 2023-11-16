
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

struct Foo : public ceto::shared_object, public std::enable_shared_from_this<Foo> {

        template <typename T1>
auto foo(const T1& x) const -> void {
            const auto self = ceto::shared_from(this);
            ((std::cout << "hi") << x) << (&self) -> use_count();
        }

        ~Foo() {
            std::cout << "dead";
        }

};

    auto main() -> int {
struct Inner : public ceto::shared_object, public std::enable_shared_from_this<Inner> {

                    std::shared_ptr<const Foo> f;

                inline auto foo(const int  x) const -> void {
                    std::cout << "hi";
                    ceto::mado(f)->foo(x);
                }

            explicit Inner(std::shared_ptr<const Foo> f) : f(std::move(f)) {}

            Inner() = delete;

        };

        const auto x = 1;
        const auto f = std::make_shared<const decltype(Foo())>();
        [x = ceto::default_capture(x), f = ceto::default_capture(f)]() {
                if constexpr (!std::is_void_v<decltype(ceto::mado(f)->foo(x))>) { return ceto::mado(f)->foo(x); } else { static_cast<void>(ceto::mado(f)->foo(x)); };
                }();
        const auto i = std::make_shared<const decltype(Inner{f})>(f);
        [x = ceto::default_capture(x), i = ceto::default_capture(i)]() {
                if constexpr (!std::is_void_v<decltype(ceto::mado(i)->foo(x))>) { return ceto::mado(i)->foo(x); } else { static_cast<void>(ceto::mado(i)->foo(x)); };
                }();
    }

