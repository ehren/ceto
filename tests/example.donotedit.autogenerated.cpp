
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
            ((std::cout << "size: ") << ceto::mado(param)->size()) << "\n";
            return self;
        }

        inline auto size() const -> auto {
            return ceto::mado(this -> data_member)->size();
        }

    explicit Foo(ceto__private__C3 data_member) : data_member(std::move(data_member)) {}

    Foo() = delete;

};

    inline auto string_join(const std::vector<std::string>&  vec, const decltype(std::string {", "})&  sep = std::string {", "}) -> std::string {
        static_assert(std::is_same_v<decltype(vec),const std::vector<std::string> &>);
        static_assert(std::is_same_v<decltype(sep),const std::string &>);
        if (ceto::mado(vec)->empty()) {
            return "";
        }
        return std::accumulate(ceto::mado(vec)->cbegin() + 1, ceto::mado(vec)->cend(), ceto::maybe_bounds_check_access(vec,0), [&sep](const auto &a, const auto &b) {
                if constexpr (!std::is_void_v<decltype(((a + sep) + b))>) { return ((a + sep) + b); } else { static_cast<void>(((a + sep) + b)); };
                });
    }

;
struct Oops : public std::runtime_error {

using std::runtime_error::runtime_error;

};

template <typename ceto__private__C4>struct Holder : public ceto::object {

    ceto__private__C4 args;

    explicit Holder(ceto__private__C4 args) : args(std::move(args)) {}

    Holder() = delete;

};

    auto main(const int  argc,  const char * const *  argv) -> int {
        auto args { std::vector<decltype(std::string(std::declval<std::ranges::range_value_t<decltype(std::span(argv, std::declval<int>()))>>()))>() } ;
        for(const auto& a : std::span(argv, argc)) {
            ceto::mad(args)->push_back(std::string(a));
        }
        const auto more = [&]() {if (argc == 0) {
            return std::string {"no args"};
        } else if ((argc > 15)) {
            throw Oops{"too many args entirely"};
        } else {
            return std::string {"end"};
        }}()
;
        ceto::mad(args)->push_back(more);
        const auto summary = string_join(args, ", ");
        const auto f = std::make_shared<const decltype(Foo{summary})>(summary);
        ceto::mado(f)->method(args);
        ceto::mado(f)->method(f);
        auto t { std::thread([f = ceto::default_capture(f)]() -> void {
                const auto d = ceto::mado(ceto::mado(f)->method(f))->data_member;
                ((std::cout << [&]() {if (ceto::mado(d)->size() < 100) {
                    return d;
                } else {
                    return std::string {"too much data!"};
                }}()
) << std::endl);
                }) } ;
        ceto::mado(t)->join();
        auto holder = std::make_unique<const decltype(Holder{args})>(args);
        auto holders { std::vector<std::unique_ptr<const decltype(Holder{args})>>() } ;
        ceto::mad(holders)->push_back(std::move(holder));
        (std::cout << ceto::mado(ceto::mado(ceto::maybe_bounds_check_access(holders,0))->args)->size()) << "\n";
    }

