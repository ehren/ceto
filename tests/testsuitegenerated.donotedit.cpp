
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
// unsafe;
struct Foo : public ceto::shared_object, public std::enable_shared_from_this<Foo> {

    int x { 0 } ; static_assert(std::is_convertible_v<decltype(0), decltype(x)>);

        inline auto bar() const -> void {
            printf("bar %d\n", this -> x);
        }

        ~Foo() {
            printf("dead\n");
        }

        inline auto operator==(const ceto::nonullpropconst<std::shared_ptr<const Foo>>&  other) const -> auto {
            printf("in == method - both foo\n");
            return ((this -> x) == (*ceto::mad(other)).x);
        }

        template <typename ceto__private__T11>
auto operator==(const ceto__private__T11& other) const -> auto {
            printf("in == method - other not foo\n");
            return (other == 5);
        }

};

    template <typename ceto__private__T22>
auto operator==(const ceto::nonullpropconst<std::shared_ptr<const Foo>>&  f, const ceto__private__T22& other) -> auto {
        return (*ceto::mad(f)).operator==(other);
    }

    inline auto operator==(const ceto::nonullpropconst<std::shared_ptr<const Foo>>&  f, const ceto::nonullpropconst<std::shared_ptr<const Foo>>&  otherfoo) -> auto {
        return (*ceto::mad(f)).operator==(otherfoo);
    }

    inline auto operator==(const ceto::nonullpropconst<std::shared_ptr<const Foo>>&  f, const std::nullptr_t  other) -> auto {
        return !f;
    }

    auto main() -> int {
        const auto f = ceto::make_shared_nonullpropconst<const Foo>();
        (*ceto::mad(f)).bar();
        if (f == 5) {
            printf("overload == works\n");
        }
        const auto b = ceto::make_shared_nonullpropconst<const Foo>();
        if (f == b) {
            printf("same\n");
        } else {
            printf("not same\n");
        }
        const ceto::nonullpropconst<std::shared_ptr<const Foo>> f2 = nullptr; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(nullptr), std::remove_cvref_t<decltype(f2)>>);
        printf("testing for null...\n");
        if (f2 == nullptr) {
            printf("we're dead\n");
        }
        if (!f2) {
            printf("we're dead\n");
        }
    }

