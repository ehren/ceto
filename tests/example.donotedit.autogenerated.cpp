
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

//#include <concepts>
//#include <ranges>
//#include <numeric>


#include "ceto.h"


#include <numeric>
;
#include <thread>
;
#include <ranges>
;
#include <iostream>
;
template <typename ceto__private__C3>struct Foo : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C3 data_member;

        template <typename T1>
auto method(const T1& param) const -> auto {
            const auto self = ceto::shared_from(this);
            (std::cout << (*ceto::mad(param)).size()) << "\n";
            return self;
        }

        inline auto size() const -> auto {
            return (*ceto::mad(this -> data_member)).size();
        }

    explicit Foo(ceto__private__C3 data_member) : data_member(std::move(data_member)) {}

    Foo() = delete;

};

    template <typename T1>
auto calls_method(const T1& f) -> auto {
        return (*ceto::mad(f)).method(f);
    }

    inline auto string_join(const std::vector<std::string>&  vec, const decltype(std::string {", "})&  sep = std::string {", "}) -> std::string {
        static_assert(std::is_same_v<decltype(vec),const std::vector<std::string> &>);
        static_assert(std::is_same_v<decltype(sep),const std::string &>);
        if ((*ceto::mad(vec)).empty()) {
            return "";
        }
        return std::accumulate((*ceto::mad(vec)).cbegin() + 1, (*ceto::mad(vec)).cend(), ceto::maybe_bounds_check_access(vec,0), [&sep](const auto &a, const auto &b) {
                if constexpr (!std::is_void_v<decltype(((a + sep) + b))>) { return ((a + sep) + b); } else { static_cast<void>(((a + sep) + b)); };
                });
    }

;
struct Oops : public std::runtime_error {

using std::runtime_error::runtime_error;

};

struct UniqueFoo : public ceto::object {

    std::vector<std::unique_ptr<const UniqueFoo>> consumed = std::vector<std::unique_ptr<const UniqueFoo>>{}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<std::unique_ptr<const UniqueFoo>>{}), std::remove_cvref_t<decltype(consumed)>>);

        inline auto consuming_method( std::unique_ptr<const UniqueFoo>  u) -> void {
            (*ceto::mad(this -> consumed)).push_back(std::move(u));
        }

        inline auto size() const -> auto {
            return (*ceto::mad(this -> consumed)).size();
        }

};

    inline auto consuming_function( std::unique_ptr<const UniqueFoo>  u) -> void {
        (*ceto::mad(std::make_shared<const decltype(Foo{42})>(42))).method(u);
        (std::cout << (*ceto::mad((*ceto::mad(u)).consumed)).size()) << std::endl;
    }

    auto main(const int  argc,  const char * const *  argv) -> int {
        auto args { std::vector<decltype(std::string(std::declval<std::ranges::range_value_t<decltype(std::span(argv, std::declval<int>()))>>()))>() } ;
        for(const auto& a : std::span(argv, argc)) {
            (*ceto::mad(args)).push_back(std::string(a));
        }
        const auto more = [&]() {if (argc == 0) {
            return std::string {"no args"};
        } else if ((argc > 15)) {
            throw Oops{"too many args entirely"};
        } else {
            return std::string {"end"};
        }}()
;
        (*ceto::mad(args)).push_back(more);
        const auto summary = string_join(args, ", ");
        const auto f = std::make_shared<const decltype(Foo{summary})>(summary);
        (*ceto::mad(f)).method(args);
        (*ceto::mad(f)).method(f);
        calls_method(f);
        auto t { std::thread([f = ceto::default_capture(f)]() -> void {
                const auto d = (*ceto::mad((*ceto::mad(f)).method(f))).data_member;
                ((std::cout << [&]() {if ((*ceto::mad(d)).size() < 100) {
                    return d;
                } else {
                    return std::string {"too much data!"};
                }}()
) << std::endl);
                }) } ;
        (*ceto::mad(t)).join();
        auto u = std::make_unique<decltype(UniqueFoo())>();
        auto u2 = std::make_unique<const decltype(UniqueFoo())>();
        (*ceto::mad(u)).consuming_method(std::move(u2));
        std::unique_ptr<const UniqueFoo> u3 = std::move(u); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::move(u)), std::remove_cvref_t<decltype(u3)>>);
        consuming_function(std::move(u3));
    }

