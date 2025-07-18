
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

;
struct Foo : public ceto::object {

    int x;

    explicit Foo(int x) : x(x) {}

    Foo() = delete;

};

#if 1
    struct HoldsFooConstRef_class : public ceto::shared_object, public std::enable_shared_from_this<HoldsFooConstRef_class> {

            const Foo & foo;

        explicit HoldsFooConstRef_class(const Foo & foo) : foo(foo) {}

        HoldsFooConstRef_class() = delete;

    };

    struct HoldsFooConstRef_struct : public ceto::object {

            const Foo & foo;

        explicit HoldsFooConstRef_struct(const Foo & foo) : foo(foo) {}

        HoldsFooConstRef_struct() = delete;

    };

#endif

#if 1
    struct HoldsFooMutRef_class : public ceto::shared_object, public std::enable_shared_from_this<HoldsFooMutRef_class> {

            Foo & foo;

            inline auto uses_field() const -> void {
                const auto & blah { 5 } ;
                if (1) {
                    // unsafe;
                    (std::cout << blah) << (*ceto::mad(this -> foo)).x;
                    static_assert(std::is_reference_v<decltype(blah)>);
                }
                static_assert(std::is_reference_v<decltype(blah)>);
                static_assert(std::is_reference_v<decltype(/* unsafe: */ blah)>);
            }

        explicit HoldsFooMutRef_class(Foo & foo) : foo(foo) {}

        HoldsFooMutRef_class() = delete;

    };

    struct HoldsFooMutRef_struct : public ceto::object {

            Foo & foo;

            inline auto uses_field() const -> void {
                const auto & blah { 5 } ;
                if (1) {
                    // unsafe;
                    (std::cout << blah) << (*ceto::mad(this -> foo)).x;
                    static_assert(std::is_reference_v<decltype(blah)>);
                }
                static_assert(std::is_reference_v<decltype(blah)>);
                static_assert(std::is_reference_v<decltype(/* unsafe: */ blah)>);
            }

        explicit HoldsFooMutRef_struct(Foo & foo) : foo(foo) {}

        HoldsFooMutRef_struct() = delete;

    };

#endif

    auto main() -> int {
        if constexpr (1) {
            const auto foo = Foo{1};
            auto foomut { Foo{2} } ;
            const auto h = HoldsFooConstRef_class(foo);
            const auto h2 = HoldsFooConstRef_class(foomut);
            const auto hm = HoldsFooMutRef_class(foomut);
            (*ceto::mad((*ceto::mad(hm)).foo)).x = 5;
            std::cout << (*ceto::mad((*ceto::mad(h)).foo)).x;
            std::cout << (*ceto::mad(foomut)).x;
            std::cout << (*ceto::mad((*ceto::mad(h2)).foo)).x;
        }
        if constexpr (1) {
            const auto foo = Foo{1};
            auto foomut { Foo{2} } ;
            const auto h = HoldsFooConstRef_struct(foo);
            const auto h2 = HoldsFooConstRef_struct(foomut);
            const auto hm = HoldsFooMutRef_struct(foomut);
            (*ceto::mad((*ceto::mad(hm)).foo)).x = 5;
            std::cout << (*ceto::mad((*ceto::mad(h)).foo)).x;
            std::cout << (*ceto::mad(foomut)).x;
            std::cout << (*ceto::mad((*ceto::mad(h2)).foo)).x;
        }
    }

