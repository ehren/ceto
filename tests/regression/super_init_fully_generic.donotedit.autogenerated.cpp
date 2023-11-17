
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

template <typename _ceto_private_C1>struct Generic : public ceto::enable_shared_from_this_base_for_templates {

    _ceto_private_C1 x;

    explicit Generic(_ceto_private_C1 x) : x(std::move(x)) {}

    Generic() = delete;

};

template <typename _ceto_private_C2>struct GenericChild : public std::type_identity_t<decltype(Generic(std::declval<_ceto_private_C2>()))> {

    explicit GenericChild(_ceto_private_C2 x) : std::type_identity_t<decltype(Generic(std::declval<_ceto_private_C2>()))> (std::move(x)) {
    }

    GenericChild() = delete;

};

    auto main() -> int {
        const auto f = std::make_shared<const decltype(Generic{5})>(5);
        const auto f2 = std::make_shared<const decltype(GenericChild{"A"})>("A");
        (std::cout << ceto::mado(f)->x) << ceto::mado(f2)->x;
    }

