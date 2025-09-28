
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
#include <thread>
;
#include <chrono>
;
 // unsafe external C++: std.thread, std.this_thread
;
struct Foo : public ceto::shared_object, public std::enable_shared_from_this<Foo> {

    int x { 1 } ; static_assert(std::is_convertible_v<decltype(1), decltype(x)>);

        inline auto long_running_method() -> void {
            while ((this -> x) <= 5) {                std::cout << "in Foo: " << (this -> x) << "\n";
                std::this_thread::sleep_for(std::chrono::seconds(1));
                (this -> x) += 1;
            }
        }

        ~Foo() {
            std::cout << "Foo destruct\n";
        }

};

struct Holder : public ceto::shared_object, public std::enable_shared_from_this<Holder> {

    ceto::propagate_const<std::shared_ptr<Foo>> f = nullptr; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(nullptr), std::remove_cvref_t<decltype(f)>>);

        inline auto getter() const -> auto {
            return this -> f;
        }

};

    auto main() -> int {
        auto g { ceto::make_shared_propagate_const<Holder>() } ;
        (*ceto::mad(g)).f = ceto::make_shared_propagate_const<Foo>();
        auto t { std::thread([g = ceto::default_capture(g)]() {
                auto gm { g } ;
                return (*ceto::mad((*ceto::mad(gm)).f)).long_running_method();
                }) } ;
        std::this_thread::sleep_for(std::chrono::milliseconds(2500));
        (*ceto::mad(g)).f = nullptr;
        (*ceto::mad(t)).join();
        std::cout << "ub has occured\n";
    }

