
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

    int a { 5 } ; static_assert(std::is_convertible_v<decltype(5), decltype(a)>);

        inline auto bar() const -> auto {
             // unsafe external C++: printf
;
            printf("bar %d\n", this -> a);
            return this -> a;
        }

};

    inline auto bam( ceto::propagate_const<std::unique_ptr<const Foo>>  f) -> void {
        (*ceto::mad(f)).bar();
    }

    inline auto baz( ceto::propagate_const<std::unique_ptr<const Foo>>  f) -> void {
        (*ceto::mad(f)).bar();
        bam(std::move(f));
    }

    auto main() -> int {
        (*ceto::mad(ceto::make_unique_propagate_const<const Foo>())).bar();
        baz(ceto::make_unique_propagate_const<const Foo>());
        auto f = ceto::make_unique_propagate_const<Foo>();
        (*ceto::mad(f)).bar();
        auto f2 = ceto::make_unique_propagate_const<Foo>();
        (*ceto::mad(f2)).bar();
        baz(std::move(f2));
        auto lst { std::vector<ceto::propagate_const<std::unique_ptr<decltype(Foo())>>>() } ;
        (lst).push_back(ceto::make_unique_propagate_const<Foo>());
        f = ceto::make_unique_propagate_const<Foo>();
        (lst).push_back(std::move(f));
        (*ceto::mad(ceto::bounds_check(lst, 0))).bar();
        (*ceto::mad(ceto::bounds_check(lst, 1))).bar();
    }

