
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

template <typename _ceto_private_C1>struct Generic : ceto::shared_object {

    _ceto_private_C1 x;

    explicit Generic(_ceto_private_C1 x) : x(x) {}

    Generic() = delete;

};

template <typename _ceto_private_C2>struct GenericChild : public std::type_identity_t<decltype(Generic(std::declval<std::remove_cvref_t<_ceto_private_C2>>()))> {

    explicit GenericChild(const _ceto_private_C2& x) : std::type_identity_t<decltype(Generic(std::declval<std::remove_cvref_t<_ceto_private_C2>>()))> (x) {
    }

    GenericChild() = delete;

};

    auto main() -> int {
        const auto f = std::make_shared<const decltype(Generic{5})>(5);
        const auto f2 = std::make_shared<const decltype(GenericChild{std::string {"A"}})>(std::string {"A"});
        (std::cout << ceto::mado(f)->x) << ceto::mado(f2)->x;
    }

