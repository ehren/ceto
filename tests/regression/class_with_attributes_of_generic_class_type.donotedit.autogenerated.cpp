
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

template <typename _ceto_private_C1, typename _ceto_private_C2, typename _ceto_private_C3>struct Foo : public ceto::enable_shared_from_this_base_for_templates {

    _ceto_private_C1 a;

    _ceto_private_C2 b;

    _ceto_private_C3 c;

    explicit Foo(_ceto_private_C1 a, _ceto_private_C2 b, _ceto_private_C3 c) : a(std::move(a)), b(std::move(b)), c(std::move(c)) {}

    Foo() = delete;

};

template <typename _ceto_private_C4, typename _ceto_private_C5>struct Bar : public ceto::enable_shared_from_this_base_for_templates {

    _ceto_private_C4 a;

    _ceto_private_C5 b;

    std::shared_ptr<const Foo<decltype(a),decltype(b),decltype(b)>> f;

    explicit Bar(_ceto_private_C4 a, _ceto_private_C5 b, std::shared_ptr<const Foo<decltype(a),decltype(b),decltype(b)>> f) : a(std::move(a)), b(std::move(b)), f(f) {}

    Bar() = delete;

};

template <typename _ceto_private_C6, typename _ceto_private_C7>struct Bar2 : public ceto::enable_shared_from_this_base_for_templates {

    _ceto_private_C6 a;

    _ceto_private_C7 b;

    decltype(std::make_shared<const decltype(Foo{b, b, b})>(b, b, b)) f;

    explicit Bar2(_ceto_private_C6 a, _ceto_private_C7 b, decltype(std::make_shared<const decltype(Foo{b, b, b})>(b, b, b)) f) : a(std::move(a)), b(std::move(b)), f(f) {}

    Bar2() = delete;

};

template <typename _ceto_private_C8>struct MixedGenericConcrete : public ceto::enable_shared_from_this_base_for_templates {

    _ceto_private_C8 a;

    int b;

    explicit MixedGenericConcrete(_ceto_private_C8 a, int b) : a(std::move(a)), b(b) {}

    MixedGenericConcrete() = delete;

};

    auto main() -> int {
        const auto f = std::make_shared<const decltype(Foo{1, 2, 3})>(1, 2, 3);
        const auto f2 = std::make_shared<const decltype(Foo{1, 2, std::vector {3}})>(1, 2, std::vector {3});
        const auto f4 = std::make_shared<const decltype(Foo{1, 2, std::make_shared<const decltype(Foo{1, 2, 3})>(1, 2, 3)})>(1, 2, std::make_shared<const decltype(Foo{1, 2, 3})>(1, 2, 3));
        const auto f5 = std::make_shared<const decltype(Foo{1, 2, std::make_shared<const decltype(Foo{1, std::make_shared<const decltype(Foo{1, 2, std::make_shared<const decltype(Foo{1, 2, 3001})>(1, 2, 3001)})>(1, 2, std::make_shared<const decltype(Foo{1, 2, 3001})>(1, 2, 3001)), std::make_shared<const decltype(Foo{1, 2, 3})>(1, 2, 3)})>(1, std::make_shared<const decltype(Foo{1, 2, std::make_shared<const decltype(Foo{1, 2, 3001})>(1, 2, 3001)})>(1, 2, std::make_shared<const decltype(Foo{1, 2, 3001})>(1, 2, 3001)), std::make_shared<const decltype(Foo{1, 2, 3})>(1, 2, 3))})>(1, 2, std::make_shared<const decltype(Foo{1, std::make_shared<const decltype(Foo{1, 2, std::make_shared<const decltype(Foo{1, 2, 3001})>(1, 2, 3001)})>(1, 2, std::make_shared<const decltype(Foo{1, 2, 3001})>(1, 2, 3001)), std::make_shared<const decltype(Foo{1, 2, 3})>(1, 2, 3)})>(1, std::make_shared<const decltype(Foo{1, 2, std::make_shared<const decltype(Foo{1, 2, 3001})>(1, 2, 3001)})>(1, 2, std::make_shared<const decltype(Foo{1, 2, 3001})>(1, 2, 3001)), std::make_shared<const decltype(Foo{1, 2, 3})>(1, 2, 3)));
        (std::cout << ceto::mado(ceto::mado(ceto::mado(ceto::mado(f5)->c)->b)->c)->c) << "\n";
        const auto b = std::make_shared<const decltype(Bar{1, 2, f})>(1, 2, f);
        (((((std::cout << ceto::mado(b)->a) << ceto::mado(b)->b) << ceto::mado(ceto::mado(b)->f)->a) << ceto::mado(ceto::mado(b)->f)->b) << ceto::mado(ceto::mado(b)->f)->c) << "\n";
        const auto b2 = std::make_shared<const decltype(Bar2{std::string {"hi"}, 2, std::make_shared<const decltype(Foo{2, 3, 4})>(2, 3, 4)})>(std::string {"hi"}, 2, std::make_shared<const decltype(Foo{2, 3, 4})>(2, 3, 4));
        (((((std::cout << ceto::mado(b2)->a) << ceto::mado(b2)->b) << ceto::mado(ceto::mado(b2)->f)->a) << ceto::mado(ceto::mado(b2)->f)->b) << ceto::mado(ceto::mado(b2)->f)->c) << "\n";
        const auto m = std::make_shared<const decltype(MixedGenericConcrete{std::string {"e"}, 2})>(std::string {"e"}, 2);
        ((std::cout << ceto::mado(m)->a) << ceto::mado(m)->b) << "\n";
    }

struct HasGenericList : public ceto::shared_object, public std::enable_shared_from_this<HasGenericList> {

};

