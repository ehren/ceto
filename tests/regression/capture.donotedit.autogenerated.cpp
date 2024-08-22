
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
                    (*ceto::mad(this -> f)).foo(x);
                }

            explicit Inner(std::shared_ptr<const Foo> f) : f(std::move(f)) {}

            Inner() = delete;

        };

        const auto x = 1;
        const auto f = std::make_shared<const decltype(Foo())>();
        const auto l = [x = ceto::default_capture(x), f = ceto::default_capture(f)]() {
                if constexpr (!std::is_void_v<decltype((*ceto::mad(f)).foo(x))>) { return (*ceto::mad(f)).foo(x); } else { static_cast<void>((*ceto::mad(f)).foo(x)); };
                };
        l();
        const auto i = std::make_shared<const decltype(Inner{f})>(f);
        [&x = std::as_const(x), &i = std::as_const(i)]() {
                if constexpr (!std::is_void_v<decltype((*ceto::mad(i)).foo(x))>) { return (*ceto::mad(i)).foo(x); } else { static_cast<void>((*ceto::mad(i)).foo(x)); };
                }();
    }

