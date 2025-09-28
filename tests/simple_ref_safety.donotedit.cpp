
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
struct HoldsRef : public ceto::object {

    int & x;

    explicit HoldsRef(int & x) : x(x) {}

    HoldsRef() = delete;

};

struct Foo : public ceto::object {

    std::vector<int> vec;

        template <typename ceto__private__T11>
auto foo(const ceto__private__T11& x) -> void {
            ceto::safe_for_loop<!std::is_reference_v<decltype(std::ranges::iota_view(0, std::ssize(this -> vec)))> && ceto::OwningContainer<std::remove_cvref_t<decltype(std::ranges::iota_view(0, std::ssize(this -> vec)))>>>(std::ranges::iota_view(0, std::ssize(this -> vec)), [&](auto &&ceto__private__lambda_param2) -> ceto::LoopControl {
    const auto i = ceto__private__lambda_param2;
                ceto::append_or_push_back(this -> vec, [&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(i)> ) && true)  )); return i; }());
    return ceto::LoopControl::Continue;
});            std::cout << x << std::endl;
        }

        inline auto good() -> void {
            const auto val = ceto::bounds_check(this -> vec, 0);
            this -> foo(val);
        }

        inline auto bad() -> void {
            this -> foo(/* unsafe: */ (ceto::bounds_check(this -> vec, 0)));
            auto & r { ceto::bounds_check(this -> vec, 0) } ;
            this -> foo(/* unsafe: */ (r));
             // unsafe external C++: std.ref
;
            this -> foo(std::ref([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(ceto::bounds_check(this -> vec, 0))> ) && true)  || true )); return ceto::bounds_check(this -> vec, 0); }()));
            this -> foo(std::ref(/* unsafe: */ (r)));
            std::cout << (*ceto::mad([]() {
                    const auto x = 5;
                    return std::ref(x);
                    }())).get();
            std::cout << (*ceto::mad([]() {
                    auto x { 5 } ;
                    return /* unsafe: */ (HoldsRef{x});
                    }())).x;
        }

    explicit Foo(std::vector<int> vec) : vec(std::move(vec)) {}

    Foo() = delete;

};

    auto main() -> int {
        auto f { Foo{std::vector {{1, 2, 3, 4}}} } ;
        (*ceto::mad(f)).good();
        (*ceto::mad(f)).bad();
    }

