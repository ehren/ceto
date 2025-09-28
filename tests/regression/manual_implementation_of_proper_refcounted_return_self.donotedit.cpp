
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
 // unsafe external C++: std.static_pointer_cast, shared_from_this, ceto.get_underlying
;
// unsafe;
template <typename ceto__private__C1>struct A : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C1 a;

    explicit A(ceto__private__C1 a) : a(std::move(a)) {}

    A() = delete;

};

struct S : public ceto::shared_object, public std::enable_shared_from_this<S> {

        inline auto foo() const -> auto {
            return std::static_pointer_cast<std::type_identity_t<ceto::propagate_const<std::shared_ptr<const S>>> :: element_type>(shared_from_this());
        }

        inline auto foo2() const -> ceto::propagate_const<std::shared_ptr<const S>> {
            return std::static_pointer_cast<std::remove_reference<decltype(*this)> :: type>(shared_from_this());
            return std::static_pointer_cast<std::remove_reference<decltype(*this)> :: type>(shared_from_this());
        }

};

    auto main() -> int {
        const auto s = ceto::make_shared_propagate_const<const S>();
        std::cout << (&ceto::get_underlying(s)) -> use_count() << std::endl;
        const auto s2 = (*ceto::mad(s)).foo();
        std::cout << (&s2) -> use_count() << std::endl;
        const auto a = ceto::make_shared_propagate_const<const decltype(A{s})>(s);
        std::cout << (&s2) -> use_count() << std::endl;
        const auto s3 = (*ceto::mad((*ceto::mad(a)).a)).foo2();
        std::cout << (&ceto::get_underlying(s)) -> use_count() << std::endl;
        std::cout << (&ceto::get_underlying(s3)) -> use_count() << std::endl;
    }

