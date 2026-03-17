
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
struct Foo : public ceto::shared_object, public std::enable_shared_from_this<Foo> {

    int x;

    explicit Foo(int x) : x(x) {}

    Foo() = delete;

};

    auto main() -> int {
        std::optional<ceto::propagate_const<std::shared_ptr<const Foo>>> f = ceto::make_shared_propagate_const<Foo>(1); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(ceto::make_shared_propagate_const<Foo>(1)), std::remove_cvref_t<decltype(f)>>);
        f = CETO_NONE;
        std::cout << !f << (f == CETO_NONE);
        const std::optional<ceto::propagate_const<std::shared_ptr<Foo>>> f_mutable_but_not_reasignable = ceto::make_shared_propagate_const<Foo>(1); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(ceto::make_shared_propagate_const<Foo>(1)), std::remove_cvref_t<decltype(f_mutable_but_not_reasignable)>>);
        const std::optional<ceto::propagate_const<std::shared_ptr<Foo>>> f_mutable_but_not_reasignable2 = ceto::make_shared_propagate_const<Foo>(1); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(ceto::make_shared_propagate_const<Foo>(1)), std::remove_cvref_t<decltype(f_mutable_but_not_reasignable2)>>);
        static_assert(std::is_same_v<decltype(f_mutable_but_not_reasignable),decltype(f_mutable_but_not_reasignable2)>);
        auto mut_alias { f_mutable_but_not_reasignable } ;
        (*ceto::mad(mut_alias)).x = 8;
        std::cout << (*ceto::mad(f_mutable_but_not_reasignable)).x;
        std::optional<ceto::propagate_const<std::shared_ptr<Foo>>> f_fully_mut = ceto::make_shared_propagate_const<Foo>(1); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(ceto::make_shared_propagate_const<Foo>(1)), std::remove_cvref_t<decltype(f_fully_mut)>>);
        (*ceto::mad(f_fully_mut)).x = 5;
        std::cout << (*ceto::mad(f_fully_mut)).x;
        f_fully_mut = CETO_NONE;
        if (f_fully_mut) {
            (*ceto::mad(f_fully_mut)).x = 20;
        }
        auto f_mut { ceto::make_shared_propagate_const<Foo>(2) } ;
        (*ceto::mad(f_mut)).x = 5;
        f_mut = (*ceto::mad_smartptr(f_mutable_but_not_reasignable)).value();
         // unsafe external C++: std.move
;
        f = std::move(f_mut);
        std::cout << (*ceto::mad(f)).x;
         // unsafe external C++: ceto.get_underlying
;
        std::cout << (ceto::get_underlying(f_mut) == nullptr);
         // unsafe external C++: std.shared_ptr, std.make_shared
;
        const auto raw_shared_ptr = std::shared_ptr<Foo>();
        const auto non_empty_raw = std::make_shared<Foo>(1);
        f = non_empty_raw;
        std::cout << (*ceto::mad(f)).x;
    }

