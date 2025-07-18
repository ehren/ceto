
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
#include "ceto_private_listcomp.donotedit.autogenerated.h"
;
#include "ceto_private_boundscheck.donotedit.autogenerated.h"
;
#include "ceto_private_convenience.donotedit.autogenerated.h"
;
#include "ceto_private_append_to_pushback.donotedit.autogenerated.h"
;
template <typename ceto__private__C1>struct FooGeneric : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C1 a;

    explicit FooGeneric(ceto__private__C1 a) : a(std::move(a)) {}

    FooGeneric() = delete;

};

struct FooConcrete : public ceto::shared_object, public std::enable_shared_from_this<FooConcrete> {

    std::string a;

    explicit FooConcrete(std::string a) : a(std::move(a)) {}

    FooConcrete() = delete;

};

template <typename ceto__private__C2>struct FooGenericUnique : public ceto::object {

    ceto__private__C2 a;

    explicit FooGenericUnique(ceto__private__C2 a) : a(std::move(a)) {}

    FooGenericUnique() = delete;

};

struct FooConcreteUnique : public ceto::object {

    std::string a;

    explicit FooConcreteUnique(std::string a) : a(std::move(a)) {}

    FooConcreteUnique() = delete;

};

    template <typename T1>
auto func(const T1& f) -> void {
        static_assert(std::is_const_v<std::remove_reference_t<decltype(f)>>);
        static_assert(std::is_reference_v<decltype(f)>);
        ((std::cout << "generic ") << (*ceto::mad(f)).a) << std::endl;
    }

    inline auto func(const ceto::propagate_const<std::shared_ptr<const FooConcrete>>&  f) -> void {
        static_assert(std::is_const_v<std::remove_reference_t<decltype(f)>>);
        static_assert(std::is_reference_v<decltype(f)>);
        ((std::cout << "FooConcrete ") << (*ceto::mad(f)).a) << std::endl;
    }

    inline auto func( ceto::propagate_const<std::unique_ptr<const FooConcreteUnique>>  f) -> void {
        static_assert(!std::is_reference_v<decltype(f)>);
        ((std::cout << "FooConcreteUnique ") << (*ceto::mad(f)).a) << std::endl;
    }

    inline auto func2( const ceto::propagate_const<std::unique_ptr<const FooConcreteUnique>>&  f) -> void {
        static_assert(std::is_const_v<std::remove_reference_t<decltype(f)>>);
        static_assert(std::is_reference_v<decltype(f)>);
        static_assert(std::is_same_v<decltype(f),const std::unique_ptr<const FooConcreteUnique> &>);
        ((std::cout << "FooConcreteUnique ") << (*ceto::mad(f)).a) << std::endl;
    }

    inline auto byval(const auto  f) -> void {
        static_assert(!std::is_reference_v<decltype(f)>);
        ((std::cout << "byval ") << (*ceto::mad(f)).a) << "\n";
    }

    auto main() -> int {
        const auto f = ceto::make_shared_propagate_const<const decltype(FooGeneric{std::string {"yo"}})>(std::string {"yo"});
        const auto f2 = ceto::make_shared_propagate_const<const FooConcrete>(std::string {"hi"});
        func(f);
        func(f2);
        func(ceto::make_unique_propagate_const<const decltype(FooGenericUnique{std::string {"hi"}})>(std::string {"hi"}));
        auto f3 = ceto::make_unique_propagate_const<const FooConcreteUnique>(std::string {"hey"});
        auto f4 = ceto::make_unique_propagate_const<FooConcreteUnique>(std::string {"hello"});
        (std::cout << (*ceto::mad(f3)).a) << "\n";
        func(f4);
        func(ceto::make_unique_propagate_const<const FooConcreteUnique>(std::string {"yo"}));
        byval(std::move(f4));
    }

