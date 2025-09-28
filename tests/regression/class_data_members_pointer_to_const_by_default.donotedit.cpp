
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

;

;

;
#include "ceto_private_listcomp.donotedit.h"
;
#include "ceto_private_boundscheck.donotedit.h"
;
#include "ceto_private_convenience.donotedit.h"
;
#include "ceto_private_append_to_pushback.donotedit.h"
;
template <typename ceto__private__C1>struct Foo : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C1 a;

        inline auto mutmethod() -> auto {
            (this -> a) = ((this -> a) + 1);
            return this -> a;
        }

        inline auto constmethod() const -> auto {
            return "i'm const by default";
        }

    explicit Foo(ceto__private__C1 a) : a(std::move(a)) {}

    Foo() = delete;

};

template <typename ceto__private__C2>struct Holder : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C2 f;

    explicit Holder(ceto__private__C2 f) : f(std::move(f)) {}

    Holder() = delete;

};

    auto main() -> int {
        const auto f = ceto::make_shared_propagate_const<const decltype(Foo{1})>(1);
        const auto h = ceto::make_shared_propagate_const<const decltype(Holder{f})>(f);
        std::cout << (*ceto::mad((*ceto::mad(h)).f)).constmethod();
        auto f2 { ceto::make_shared_propagate_const<decltype(Foo{2})>(2) } ;
        (*ceto::mad(f2)).mutmethod();
        const auto h2 = ceto::make_shared_propagate_const<const decltype(Holder{f2})>(f2);
        auto f2_mut_copy { (*ceto::mad(h2)).f } ;
        (*ceto::mad(f2_mut_copy)).mutmethod();
    }

