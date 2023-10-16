
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

template <typename _ceto_private_C1>struct Foo : ceto::shared_object {

    _ceto_private_C1 a;

        inline auto f() const -> void {
            const auto self = ceto::shared_from(this);
            (std::cout << (this -> a)) << std::string {"\n"};
            ((std::cout << std::string {"in f:"}) << (&self) -> use_count()) << std::string {"\n"};
        }

        inline auto f2() const -> void {
            const auto self = ceto::shared_from(this);
            (std::cout << (this -> a)) << std::string {"\n"};
            ((std::cout << std::string {"in f2:"}) << (&self) -> use_count()) << std::string {"\n"};
            const auto outer = [self = ceto::default_capture(self)]() {
                    ((std::cout << std::string {"in lambda1:"}) << (&self) -> use_count()) << std::string {"\n"};
                    const auto l = [self = ceto::default_capture(self)]() {
                            (std::cout << ceto::mado(self)->a) << std::string {"\n"};
                            return;
                            };
                    l();
                    ((std::cout << std::string {"in lambda2:"}) << (&self) -> use_count()) << std::string {"\n"};
                    return;
                    };
            outer();
            ((std::cout << std::string {"in f2:"}) << (&self) -> use_count()) << std::string {"\n"};
        }

        ~Foo() {
            std::cout << std::string {"dead\n"};
        }

    explicit Foo(_ceto_private_C1 a) : a(a) {}

    Foo() = delete;

};

    auto main() -> int {
        ceto::mado(std::make_shared<const decltype(Foo{std::string {"yo"}})>(std::string {"yo"}))->f();
        ceto::mado(std::make_shared<const decltype(Foo{std::string {"yo"}})>(std::string {"yo"}))->f2();
    }

