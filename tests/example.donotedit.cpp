
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
#include <numeric>
;
#include <ranges>
;
#include <iostream>
;
#include <future>
;
template <typename ceto__private__C1>struct Foo : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C1 data_member;

        template <typename ceto__private__T12>
auto method(const ceto__private__T12& param) const -> auto {
            const auto self = ceto::shared_from(this);
            std::cout << (*ceto::mad(param)).size() << "\n";
            return self;
        }

        inline auto size() const -> auto {
            return (*ceto::mad(this -> data_member)).size();
        }

    explicit Foo(ceto__private__C1 data_member) : data_member(std::move(data_member)) {}

    Foo() = delete;

};

    template <typename ceto__private__T13>
auto calls_method(const ceto__private__T13& f) -> auto {
        return (*ceto::mad(f)).method(f);
    }

struct UniqueFoo : public ceto::object {

    std::vector<ceto::propagate_const<std::unique_ptr<const UniqueFoo>>> consumed = std::vector<ceto::propagate_const<std::unique_ptr<const UniqueFoo>>>{}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<ceto::propagate_const<std::unique_ptr<const UniqueFoo>>>{}), std::remove_cvref_t<decltype(consumed)>>);

        inline auto size() const -> auto {
            return (*ceto::mad(this -> consumed)).size();
        }

        inline auto consuming_method( ceto::propagate_const<std::unique_ptr<const UniqueFoo>>  u) -> void {
            (*ceto::mad(ceto::make_shared_propagate_const<const decltype(Foo{42})>(42))).method(u);
            (*ceto::mad(this -> consumed)).push_back(std::move(u));
        }

};

    inline auto string_join(const std::vector<std::string>&  vec, const decltype(std::string {", "})& sep = std::string {", "}) -> std::string {
        static_assert(std::is_same_v<decltype(vec),const std::vector<std::string> &>);
        static_assert(std::is_same_v<decltype(sep),const std::string &>);
        if ((*ceto::mad(vec)).empty()) {
            return "";
        }
         // unsafe external C++: std.accumulate
;
        if (1) {
// Unsafe
            return std::accumulate((*ceto::mad(vec)).cbegin() + 1, (*ceto::mad(vec)).cend(), ceto::bounds_check(vec, 0), [&sep](const auto &a, const auto &b) {
                    return (a + sep + b);
                    });
};
    }


;
    auto main(const int  argc, const char * *  argv) -> int {
         // unsafe external C++: std.span, std.async, std.launch.async, std.thread
;
        const auto args = []( auto &&  ceto__private__ident__2) {
                auto ceto__private__ident__1 { std::vector<std::remove_cvref_t<decltype(std::string(std::declval<std::ranges::range_value_t<decltype(ceto__private__ident__2)>>()))>>() } ;
                ceto::util::maybe_reserve(ceto__private__ident__1, ceto__private__ident__2);
                
    
                    static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__ident__2)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                    size_t ceto__private__size5 = std::size(ceto__private__ident__2);
                    for (size_t ceto__private__idx4 = 0; ; ceto__private__idx4++) {
                        if (std::size(ceto__private__ident__2) != ceto__private__size5) {
                            std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                            std::terminate();
                        }
                        if (ceto__private__idx4 >= ceto__private__size5) {
                            break ;
                        }
                        const auto a = ceto__private__ident__2[ceto__private__idx4];
                                            (ceto__private__ident__1).push_back(std::string([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(a)> ) && true)  || true || ceto::IsContainer<std::remove_cvref_t<decltype(ceto__private__ident__1)>>)); return a; }()));

                    }
                    return ceto__private__ident__1;
                }([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(std::span(/* unsafe: */ (argv), argc))> ) && true) || ceto::IsStateless<std::remove_cvref_t<decltype([]( auto &&  ceto__private__ident__2) {
        auto ceto__private__ident__1 { std::vector<std::remove_cvref_t<decltype(std::string(std::declval<std::ranges::range_value_t<decltype(ceto__private__ident__2)>>()))>>() } ;
        ceto::util::maybe_reserve(ceto__private__ident__1, ceto__private__ident__2);
        
    
            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__ident__2)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size7 = std::size(ceto__private__ident__2);
            for (size_t ceto__private__idx6 = 0; ; ceto__private__idx6++) {
                if (std::size(ceto__private__ident__2) != ceto__private__size7) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx6 >= ceto__private__size7) {
                    break ;
                }
                const auto a = ceto__private__ident__2[ceto__private__idx6];
                            (ceto__private__ident__1).push_back(std::string([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(a)> ) && true)  || true || ceto::IsContainer<std::remove_cvref_t<decltype(ceto__private__ident__1)>>)); return a; }()));

            }
            return ceto__private__ident__1;
        })>> )); return std::span(/* unsafe: */ (argv), argc); }());
        const auto summary = string_join(args, ", ");
        const auto f = ceto::make_shared_propagate_const<const decltype(Foo{summary})>(summary);
        (*ceto::mad(f)).method(args);
        (*ceto::mad(f)).method(f);
        calls_method(f);
        auto fut { std::async(std::launch::async, [f = ceto::default_capture(f)]() {
                return (*ceto::mad(f)).method(f);
                }) } ;
        (*ceto::mad((*ceto::mad(fut)).get())).method(f);
        auto thread { std::thread([f = ceto::default_capture(f)]() {
                std::cout << (*ceto::mad(f)).size();
                return (*ceto::mad(f)).method(f);
                }) } ;
        (*ceto::mad(thread)).join();
        auto u = ceto::make_unique_propagate_const<UniqueFoo>();
        auto u2 = ceto::make_unique_propagate_const<const UniqueFoo>();
        (*ceto::mad(u)).consuming_method(std::move(u2));
        (*ceto::mad(u)).consuming_method(std::move(u));
    }

