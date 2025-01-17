
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


#include "ceto.h"
//#include "ceto_private_boundscheck.donotedit.autogenerated.h"

#include "ceto_private_listcomp.donotedit.autogenerated.h"
;
#include "ceto_private_boundscheck.donotedit.autogenerated.h"
;
#include "ceto_private_convenience.donotedit.autogenerated.h"
;
    template <typename T1>
auto bad(const T1& a,  auto &  b) -> void {
        return;
        for(const auto& x : a) {
            (*ceto::mad(b)).push_back(1337);
            std::cout << x;
        }
    }

    template <typename T1>
auto bad2(const T1& a,  auto &  b) -> void {
        return;
        const auto begin = (*ceto::mad(a)).cbegin();
        const auto end = (*ceto::mad(a)).cend();
        (*ceto::mad(b)).clear();
        std::cout << (std::find(begin, end, 3) != end);
    }

struct Foo : public ceto::shared_object, public std::enable_shared_from_this<Foo> {

    decltype(std::vector {{1, 2, 3}}) a = std::vector {{1, 2, 3}};

        inline auto mm() -> void {
            ; // pass
        }

        inline auto bar() const -> void {
            ; // pass
        }

        inline auto foo() const -> void {
            const auto self = ceto::shared_from(this);
            const auto a = (this -> a);
            for(const auto& x : a) {
                std::cout << x;
                std::cout << "\n";
                this -> bar();
            }
            const auto l = [self = ceto::default_capture(self)]() {
                    if constexpr (!std::is_void_v<decltype((*ceto::mad(self)).bar())>) { return (*ceto::mad(self)).bar(); } else { static_cast<void>((*ceto::mad(self)).bar()); };
                    };
            const auto s = self;
            auto && b { (this -> a) } ;
            for(const auto& x : b) {
                std::cout << x;
                this -> bar();
                l();
                (*ceto::mad(s)).bar();
            }
            const auto y = std::vector {{1, 2}};
            for(const auto& x : (this -> a)) {
                std::cout << x;
                y;
                ceto::bounds_check(y, 0);
            }
        }

        inline auto foo() -> void {
            (*ceto::mad(this -> a)).push_back(4);
            std::cout << ceto::bounds_check(this -> a, 3);
            std::cout << (std::find((*ceto::mad(this -> a)).begin(), (*ceto::mad(this -> a)).end(), 1) != (*ceto::mad(this -> a)).end());
        }

};

struct Blah : public ceto::shared_object, public std::enable_shared_from_this<Blah> {

    std::shared_ptr<Foo> foo = std::make_shared<Foo>(); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::make_shared<Foo>()), std::remove_cvref_t<decltype(foo)>>);

};

    auto main() -> int {
        const auto f = std::make_shared<const Foo>();
        (*ceto::mad(f)).foo();
        const auto z = std::vector {{2, 3}};
        auto m { std::make_shared<Foo>() } ;
        (*ceto::mad(m)).foo();
        std::cout << ceto::bounds_check((*ceto::mad(m)).a, 3);
        const auto element = ceto::bounds_check((*ceto::mad(m)).a, 3);
        const auto ma = (*ceto::mad(m)).a;
        std::cout << element;
        const auto y = std::vector {{1, 2}};
        for(const auto& x : (*ceto::mad(m)).a) {
            const auto zma2 = ma;
            std::cout << x;
            y;
        }
        auto ma3 { (*ceto::mad(m)).a } ;
        bad(ma3, ma3);
        bad2(ma3, ma3);
        const auto b = std::make_shared<const Blah>();
        (*ceto::mad((*ceto::mad(b)).foo)).mm();
    }

