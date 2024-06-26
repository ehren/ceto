
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
#include <ranges>
;
#include <iostream>
;
#include <future>
;
template <typename ceto__private__C5>struct Foo : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C5 data_member;

        template <typename T1>
auto method(const T1& param) const -> auto {
            const auto self = ceto::shared_from(this);
            (std::cout << (*ceto::mad(param)).size()) << "\n";
            return self;
        }

        inline auto size() const -> auto {
            return (*ceto::mad(this -> data_member)).size();
        }

    explicit Foo(ceto__private__C5 data_member) : data_member(std::move(data_member)) {}

    Foo() = delete;

};

    template <typename T1>
auto calls_method(const T1& f) -> auto {
        return (*ceto::mad(f)).method(f);
    }

struct UniqueFoo : public ceto::object {

    std::vector<std::unique_ptr<const UniqueFoo>> consumed = std::vector<std::unique_ptr<const UniqueFoo>>{}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<std::unique_ptr<const UniqueFoo>>{}), std::remove_cvref_t<decltype(consumed)>>);

        inline auto size() const -> auto {
            return (*ceto::mad(this -> consumed)).size();
        }

        inline auto consuming_method( std::unique_ptr<const UniqueFoo>  u) -> void {
            (*ceto::mad(std::make_shared<const decltype(Foo{42})>(42))).method(u);
            (*ceto::mad(this -> consumed)).push_back(std::move(u));
        }

};

struct Oops : public std::runtime_error {

using std::runtime_error::runtime_error;

};

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
;
;
    auto main(const int  argc,  const char * const *  argv) -> int {
        const auto args = [&]() {
                auto result { std::vector<decltype(std::string(std::declval<std::ranges::range_value_t<decltype(std::span(argv, std::declval<int>()))>>()))>() } ;
                for(const auto& a : std::span(argv, argc)) {
                    (*ceto::mad(result)).push_back(std::string(a));
                }
                return result;
                }();
        const auto summary = string_join(args, ", ");
        const auto f = std::make_shared<const decltype(Foo{summary})>(summary);
        (*ceto::mad(f)).method(args);
        (*ceto::mad(f)).method(f);
        calls_method(f);
        const auto i = 42;
        auto fut { std::async(std::launch::async, [f = ceto::default_capture(f), i = ceto::default_capture(i)]() {
                const auto data = (*ceto::mad((*ceto::mad(f)).method(f))).data_member;
                if constexpr (!std::is_void_v<decltype([&]() {if (((*ceto::mad(data)).size() + i) < 1000) {
                    return data;
                } else {
                    throw Oops{std::string {"too much data!"}};
                }}()
)>) { return [&]() {if (((*ceto::mad(data)).size() + i) < 1000) {
                    return data;
                } else {
                    throw Oops{std::string {"too much data!"}};
                }}()
; } else { static_cast<void>([&]() {if (((*ceto::mad(data)).size() + i) < 1000) {
                    return data;
                } else {
                    throw Oops{std::string {"too much data!"}};
                }}()
); };
                }) } ;
        (std::cout << (*ceto::mad(fut)).get()) << std::endl;
        auto u = std::make_unique<decltype(UniqueFoo())>();
        auto u2 = std::make_unique<const decltype(UniqueFoo())>();
        (*ceto::mad(u)).consuming_method(std::move(u2));
        (*ceto::mad(u)).consuming_method(std::move(u));
    }

