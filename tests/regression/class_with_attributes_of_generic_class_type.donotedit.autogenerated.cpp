
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


template <typename ceto__private__C1, typename ceto__private__C2, typename ceto__private__C3>struct Foo : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C1 a;

    ceto__private__C2 b;

    ceto__private__C3 c;

    explicit Foo(ceto__private__C1 a, ceto__private__C2 b, ceto__private__C3 c) : a(std::move(a)), b(std::move(b)), c(std::move(c)) {}

    Foo() = delete;

};

template <typename ceto__private__C4, typename ceto__private__C5>struct Bar : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C4 a;

    ceto__private__C5 b;

    std::shared_ptr<const Foo<decltype(a),decltype(b),decltype(b)>> f;

    explicit Bar(ceto__private__C4 a, ceto__private__C5 b, std::shared_ptr<const Foo<decltype(a),decltype(b),decltype(b)>> f) : a(std::move(a)), b(std::move(b)), f(f) {}

    Bar() = delete;

};

template <typename ceto__private__C6, typename ceto__private__C7>struct Bar2 : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C6 a;

    ceto__private__C7 b;

    decltype(std::make_shared<const decltype(Foo{b, b, b})>(b, b, b)) f;

    explicit Bar2(ceto__private__C6 a, ceto__private__C7 b, decltype(std::make_shared<const decltype(Foo{b, b, b})>(b, b, b)) f) : a(std::move(a)), b(std::move(b)), f(f) {}

    Bar2() = delete;

};

template <typename ceto__private__C8>struct MixedGenericConcrete : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C8 a;

    int b;

    explicit MixedGenericConcrete(ceto__private__C8 a, int b) : a(std::move(a)), b(b) {}

    MixedGenericConcrete() = delete;

};

    auto main() -> int {
        const auto f = std::make_shared<const decltype(Foo{1, 2, 3})>(1, 2, 3);
        const auto f2 = std::make_shared<const decltype(Foo{1, 2, std::vector {3}})>(1, 2, std::vector {3});
        const auto f4 = std::make_shared<const decltype(Foo{1, 2, std::make_shared<const decltype(Foo{1, 2, 3})>(1, 2, 3)})>(1, 2, std::make_shared<const decltype(Foo{1, 2, 3})>(1, 2, 3));
        const auto f5 = std::make_shared<const decltype(Foo{1, 2, std::make_shared<const decltype(Foo{1, std::make_shared<const decltype(Foo{1, 2, std::make_shared<const decltype(Foo{1, 2, 3001})>(1, 2, 3001)})>(1, 2, std::make_shared<const decltype(Foo{1, 2, 3001})>(1, 2, 3001)), std::make_shared<const decltype(Foo{1, 2, 3})>(1, 2, 3)})>(1, std::make_shared<const decltype(Foo{1, 2, std::make_shared<const decltype(Foo{1, 2, 3001})>(1, 2, 3001)})>(1, 2, std::make_shared<const decltype(Foo{1, 2, 3001})>(1, 2, 3001)), std::make_shared<const decltype(Foo{1, 2, 3})>(1, 2, 3))})>(1, 2, std::make_shared<const decltype(Foo{1, std::make_shared<const decltype(Foo{1, 2, std::make_shared<const decltype(Foo{1, 2, 3001})>(1, 2, 3001)})>(1, 2, std::make_shared<const decltype(Foo{1, 2, 3001})>(1, 2, 3001)), std::make_shared<const decltype(Foo{1, 2, 3})>(1, 2, 3)})>(1, std::make_shared<const decltype(Foo{1, 2, std::make_shared<const decltype(Foo{1, 2, 3001})>(1, 2, 3001)})>(1, 2, std::make_shared<const decltype(Foo{1, 2, 3001})>(1, 2, 3001)), std::make_shared<const decltype(Foo{1, 2, 3})>(1, 2, 3)));
        (std::cout << (*ceto::mad((*ceto::mad((*ceto::mad((*ceto::mad(f5)).c)).b)).c)).c) << "\n";
        const auto b = std::make_shared<const decltype(Bar{1, 2, f})>(1, 2, f);
        (((((std::cout << (*ceto::mad(b)).a) << (*ceto::mad(b)).b) << (*ceto::mad((*ceto::mad(b)).f)).a) << (*ceto::mad((*ceto::mad(b)).f)).b) << (*ceto::mad((*ceto::mad(b)).f)).c) << "\n";
        const auto b2 = std::make_shared<const decltype(Bar2{std::string {"hi"}, 2, std::make_shared<const decltype(Foo{2, 3, 4})>(2, 3, 4)})>(std::string {"hi"}, 2, std::make_shared<const decltype(Foo{2, 3, 4})>(2, 3, 4));
        (((((std::cout << (*ceto::mad(b2)).a) << (*ceto::mad(b2)).b) << (*ceto::mad((*ceto::mad(b2)).f)).a) << (*ceto::mad((*ceto::mad(b2)).f)).b) << (*ceto::mad((*ceto::mad(b2)).f)).c) << "\n";
        const auto m = std::make_shared<const decltype(MixedGenericConcrete{std::string {"e"}, 2})>(std::string {"e"}, 2);
        ((std::cout << (*ceto::mad(m)).a) << (*ceto::mad(m)).b) << "\n";
    }

struct HasGenericList : public ceto::shared_object, public std::enable_shared_from_this<HasGenericList> {

};

