
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

        inline auto method() const -> void {
            std::cout << "method";
        }

        ~Foo() {
            std::cout << "Foo destruct";
        }

};

struct Holder : public ceto::shared_object, public std::enable_shared_from_this<Holder> {

    std::shared_ptr<const Foo> f;

    explicit Holder(std::shared_ptr<const Foo> f) : f(std::move(f)) {}

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

