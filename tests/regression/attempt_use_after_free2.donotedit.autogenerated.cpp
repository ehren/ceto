
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


#include <chrono>
;
struct Foo : public ceto::shared_object, public std::enable_shared_from_this<Foo> {

    int x { 1 } ; static_assert(std::is_convertible_v<decltype(1), decltype(x)>);

        inline auto long_running_method() -> void {
            while ((this -> x) <= 5) {                ((std::cout << "in Foo: ") << (this -> x)) << "\n";
                std::this_thread::sleep_for(std::chrono::seconds(1));
                (this -> x) += 1;
            }
        }

        ~Foo() {
            std::cout << "Foo destruct\n";
        }

};

struct Holder : public ceto::shared_object, public std::enable_shared_from_this<Holder> {

    std::shared_ptr<Foo> f = nullptr; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(nullptr), std::remove_cvref_t<decltype(f)>>);

        inline auto getter() const -> auto {
            return (this -> f);
        }

};

    auto main() -> int {
        const auto g = std::make_shared<decltype(Holder())>();
        (*ceto::mad(g)).f = std::make_shared<decltype(Foo())>();
        auto t { std::thread([g = ceto::default_capture(g)]() {
                if constexpr (!std::is_void_v<decltype((*ceto::mad((*ceto::mad(g)).f)).long_running_method())>) { return (*ceto::mad((*ceto::mad(g)).f)).long_running_method(); } else { static_cast<void>((*ceto::mad((*ceto::mad(g)).f)).long_running_method()); };
                }) } ;
        std::this_thread::sleep_for(std::chrono::milliseconds(2500));
        (*ceto::mad(g)).f = nullptr;
        (*ceto::mad(t)).join();
        std::cout << "ub has occured\n";
    }

