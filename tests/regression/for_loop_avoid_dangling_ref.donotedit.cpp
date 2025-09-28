
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
struct Foo : public ceto::object {

    decltype(std::vector {{std::vector {{std::vector {{1, 2, 3}}, std::vector {1}}}, std::vector {{std::vector {2}}}, std::vector {{std::vector {{3, 4}}, std::vector {5}}}}}) a = std::vector {{std::vector {{std::vector {{1, 2, 3}}, std::vector {1}}}, std::vector {{std::vector {2}}}, std::vector {{std::vector {{3, 4}}, std::vector {5}}}}};

        inline auto foo_method() const -> auto {
            return this -> a;
        }

};

struct Bar : public ceto::object {

    decltype(Foo()) foo = Foo();

};

    auto main() -> int {
        const auto b = Bar();
        ceto::safe_for_loop<!std::is_reference_v<decltype(std::vector([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(ceto::bounds_check(ceto::bounds_check((*ceto::mad((*ceto::mad(b)).foo)).a, 0), 0))> ) && true)  || true )); return ceto::bounds_check(ceto::bounds_check((*ceto::mad((*ceto::mad(b)).foo)).a, 0), 0); }()))> && ceto::OwningContainer<std::remove_cvref_t<decltype(std::vector([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(ceto::bounds_check(ceto::bounds_check((*ceto::mad((*ceto::mad(b)).foo)).a, 0), 0))> ) && true)  || true )); return ceto::bounds_check(ceto::bounds_check((*ceto::mad((*ceto::mad(b)).foo)).a, 0), 0); }()))>>>(std::vector([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(ceto::bounds_check(ceto::bounds_check((*ceto::mad((*ceto::mad(b)).foo)).a, 0), 0))> ) && true)  || true )); return ceto::bounds_check(ceto::bounds_check((*ceto::mad((*ceto::mad(b)).foo)).a, 0), 0); }()), [&](auto &&ceto__private__lambda_param1) -> ceto::LoopControl {
    const auto i = ceto__private__lambda_param1;
            std::cout << i;
    return ceto::LoopControl::Continue;
});        ceto::safe_for_loop<!std::is_reference_v<decltype(ceto::bounds_check(ceto::bounds_check((*ceto::mad((*ceto::mad(b)).foo)).foo_method(), 0), 0))> && ceto::OwningContainer<std::remove_cvref_t<decltype(ceto::bounds_check(ceto::bounds_check((*ceto::mad((*ceto::mad(b)).foo)).foo_method(), 0), 0))>>>(ceto::bounds_check(ceto::bounds_check((*ceto::mad((*ceto::mad(b)).foo)).foo_method(), 0), 0), [&](auto &&ceto__private__lambda_param2) -> ceto::LoopControl {
    const auto i = ceto__private__lambda_param2;
            std::cout << i;
    return ceto::LoopControl::Continue;
});    }

