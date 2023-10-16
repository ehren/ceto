
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

        inline auto method() const -> void {
            std::cout << std::string {"method"};
        }

        ~Foo() {
            std::cout << std::string {"Foo destruct"};
        }

};

struct Holder : ceto::shared_object {

    std::shared_ptr<const Foo> f;

    explicit Holder(std::shared_ptr<const Foo> f) : f(f) {}

    Holder() = delete;

};

    inline auto accessor() -> auto {
        static auto g { std::make_shared<decltype(Holder{nullptr})>(nullptr) } ;
        return g;
    }

    template <typename T1>
auto aliaser(const T1& f) -> void {
        const auto g = accessor();
        ceto::mado(g)->f = nullptr;
        std::cout << (f == nullptr);
        std::cout << (&f) -> use_count();
        std::cout << ((&f) -> get() == nullptr);
    }

    auto main() -> int {
        const auto f = accessor();
        ceto::mado(f)->f = std::make_shared<const decltype(Foo())>();
        std::cout << (&ceto::mado(f)->f) -> use_count();
        aliaser(ceto::mado(f)->f);
    }

