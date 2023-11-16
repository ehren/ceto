
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

template <typename _ceto_private_C1>struct Foo : public ceto::enable_shared_from_this_base_for_templates {

    _ceto_private_C1 a;

        inline auto f() const -> void {
            const auto self = ceto::shared_from(this);
            (std::cout << (this -> a)) << "\n";
            ((std::cout << "in f:") << (&self) -> use_count()) << "\n";
        }

        inline auto f2() const -> void {
            const auto self = ceto::shared_from(this);
            (std::cout << (this -> a)) << "\n";
            ((std::cout << "in f2:") << (&self) -> use_count()) << "\n";
            const auto outer = [self = ceto::default_capture(self)]() {
                    ((std::cout << "in lambda1:") << (&self) -> use_count()) << "\n";
                    const auto l = [self = ceto::default_capture(self)]() {
                            (std::cout << ceto::mado(self)->a) << "\n";
                            return;
                            };
                    l();
                    ((std::cout << "in lambda2:") << (&self) -> use_count()) << "\n";
                    return;
                    };
            outer();
            ((std::cout << "in f2:") << (&self) -> use_count()) << "\n";
        }

        ~Foo() {
            std::cout << "dead\n";
        }

    explicit Foo(const _ceto_private_C1& a) : a(a) {}

    Foo() = delete;

};

    auto main() -> int {
        ceto::mado(std::make_shared<const decltype(Foo{std::string {"yo"}})>(std::string {"yo"}))->f();
        ceto::mado(std::make_shared<const decltype(Foo{std::string {"yo"}})>(std::string {"yo"}))->f2();
    }

