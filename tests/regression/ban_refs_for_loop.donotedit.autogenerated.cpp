
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


;

;

;

;

;

;

;

;

;

;

;
#include "ceto_private_listcomp.donotedit.autogenerated.h"
;
#include "ceto_private_boundscheck.donotedit.autogenerated.h"
;
#include "ceto_private_convenience.donotedit.autogenerated.h"
;
#include "ceto_private_append_to_pushback.donotedit.autogenerated.h"
;
#include <algorithm>
;
    template <typename T1>
auto bad(const T1& a,  auto &  b) -> void {
        return;
        
    
            static_assert(requires { std::begin(a) + 2; }, "not a contiguous container");
            size_t ceto__private__size2 = std::size(a);
            for (size_t ceto__private__idx1 = 0; ; ceto__private__idx1++) {
                if (std::size(a) != ceto__private__size2) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx1 >= ceto__private__size2) {
                    break;
                }
                const auto x = a[ceto__private__idx1];
                            (*ceto::mad(b)).push_back(1337);
                    std::cout << x;

            }
        }

    template <typename T1>
auto bad2(const T1& a,  auto &  b) -> void {
        return;
        const auto begin = CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(a)).cbegin());
        const auto end = CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(a)).cend());
        (*ceto::mad(b)).clear();
        std::cout << (CETO_BAN_RAW_DEREFERENCABLE(std::find(begin, end, 3)) != end);
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
            
    
                static_assert(requires { std::begin(a) + 2; }, "not a contiguous container");
                size_t ceto__private__size4 = std::size(a);
                for (size_t ceto__private__idx3 = 0; ; ceto__private__idx3++) {
                    if (std::size(a) != ceto__private__size4) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx3 >= ceto__private__size4) {
                        break;
                    }
                    const auto x = a[ceto__private__idx3];
                                    std::cout << x;
                            std::cout << "\n";
                            this -> bar();

                }
                const auto l = [self = ceto::default_capture(self)]() {
                    return (*ceto::mad(self)).bar();
                    };
            const auto s = self;
            auto && b { (this -> a) } ;
            
    
                static_assert(requires { std::begin(b) + 2; }, "not a contiguous container");
                size_t ceto__private__size6 = std::size(b);
                for (size_t ceto__private__idx5 = 0; ; ceto__private__idx5++) {
                    if (std::size(b) != ceto__private__size6) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx5 >= ceto__private__size6) {
                        break;
                    }
                    const auto x = b[ceto__private__idx5];
                                    std::cout << x;
                            this -> bar();
                            l();
                            (*ceto::mad(s)).bar();

                }
                const auto y = std::vector {{1, 2}};
            
                auto&& ceto__private__intermediate7 = this -> a;

                static_assert(requires { std::begin(ceto__private__intermediate7) + 2; }, "not a contiguous container");
                size_t ceto__private__size9 = std::size(ceto__private__intermediate7);
                for (size_t ceto__private__idx8 = 0; ; ceto__private__idx8++) {
                    if (std::size(ceto__private__intermediate7) != ceto__private__size9) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx8 >= ceto__private__size9) {
                        break;
                    }
                    const auto x = ceto__private__intermediate7[ceto__private__idx8];
                                    std::cout << x;
                            y;
                            ceto::bounds_check(y, 0);

                }
            }

        inline auto foo() -> void {
            (*ceto::mad(this -> a)).push_back(4);
            std::cout << ceto::bounds_check(this -> a, 3);
            std::cout << (CETO_BAN_RAW_DEREFERENCABLE(std::find([&]() -> decltype(auto) { static_assert(((!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).begin()))>  || (!std::is_reference_v<decltype([&]() -> decltype(auto) { static_assert(((!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).end()))>  || (!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).begin()))> && std::is_fundamental_v<std::remove_cvref_t<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).begin()))>> && !std::is_reference_v<decltype(1)> && std::is_fundamental_v<std::remove_cvref_t<decltype(1)>>)) && true)); return CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).end()); }())> && std::is_fundamental_v<std::remove_cvref_t<decltype([&]() -> decltype(auto) { static_assert(((!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).end()))>  || (!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).begin()))> && std::is_fundamental_v<std::remove_cvref_t<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).begin()))>> && !std::is_reference_v<decltype(1)> && std::is_fundamental_v<std::remove_cvref_t<decltype(1)>>)) && true)); return CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).end()); }())>> && !std::is_reference_v<decltype(1)> && std::is_fundamental_v<std::remove_cvref_t<decltype(1)>>)) && true)); return CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).begin()); }(), [&]() -> decltype(auto) { static_assert(((!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).end()))>  || (!std::is_reference_v<decltype([&]() -> decltype(auto) { static_assert(((!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).begin()))>  || (!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).end()))> && std::is_fundamental_v<std::remove_cvref_t<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).end()))>> && !std::is_reference_v<decltype(1)> && std::is_fundamental_v<std::remove_cvref_t<decltype(1)>>)) && true)); return CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).begin()); }())> && std::is_fundamental_v<std::remove_cvref_t<decltype([&]() -> decltype(auto) { static_assert(((!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).begin()))>  || (!std::is_reference_v<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).end()))> && std::is_fundamental_v<std::remove_cvref_t<decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).end()))>> && !std::is_reference_v<decltype(1)> && std::is_fundamental_v<std::remove_cvref_t<decltype(1)>>)) && true)); return CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).begin()); }())>> && !std::is_reference_v<decltype(1)> && std::is_fundamental_v<std::remove_cvref_t<decltype(1)>>)) && true)); return CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).end()); }(), 1)) != CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(this -> a)).end()));
        }

};

struct Blah : public ceto::shared_object, public std::enable_shared_from_this<Blah> {

    ceto::propagate_const<std::shared_ptr<Foo>> foo = ceto::make_shared_propagate_const<Foo>(); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(ceto::make_shared_propagate_const<Foo>()), std::remove_cvref_t<decltype(foo)>>);

};

    auto main() -> int {
        const auto f = ceto::make_shared_propagate_const<const Foo>();
        (*ceto::mad(f)).foo();
        const auto z = std::vector {{2, 3}};
        auto m { ceto::make_shared_propagate_const<Foo>() } ;
        (*ceto::mad(m)).foo();
        std::cout << ceto::bounds_check((*ceto::mad(m)).a, 3);
        const auto element = ceto::bounds_check((*ceto::mad(m)).a, 3);
        const auto ma = (*ceto::mad(m)).a;
        std::cout << element;
        const auto y = std::vector {{1, 2}};
        
            auto&& ceto__private__intermediate10 = (*ceto::mad(m)).a;

            static_assert(requires { std::begin(ceto__private__intermediate10) + 2; }, "not a contiguous container");
            size_t ceto__private__size12 = std::size(ceto__private__intermediate10);
            for (size_t ceto__private__idx11 = 0; ; ceto__private__idx11++) {
                if (std::size(ceto__private__intermediate10) != ceto__private__size12) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx11 >= ceto__private__size12) {
                    break;
                }
                const auto x = ceto__private__intermediate10[ceto__private__idx11];
                            const auto zma2 = ma;
                    std::cout << x;
                    y;

            }
            auto ma3 { (*ceto::mad(m)).a } ;
        bad(ma3, ma3);
        bad2(ma3, ma3);
        const auto b = ceto::make_shared_propagate_const<const Blah>();
        (*ceto::mad((*ceto::mad(b)).foo)).mm();
    }

