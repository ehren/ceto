
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
template <typename ceto__private__C1>struct Generic : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C1 x;

    explicit Generic(ceto__private__C1 x) : x(std::move(x)) {}

    Generic() = delete;

};

template <typename ceto__private__C2>struct GenericChild : public std::type_identity_t<decltype(Generic(std::declval<ceto__private__C2>()))> {

    explicit GenericChild(ceto__private__C2 x) : std::type_identity_t<decltype(Generic(std::declval<ceto__private__C2>()))> (x) {
    }

    GenericChild() = delete;

};

    auto main() -> int {
        const auto f = ceto::make_shared_propagate_const<const decltype(Generic{5})>(5);
        const auto f2 = ceto::make_shared_propagate_const<const decltype(GenericChild{"A"})>("A");
        (std::cout << (*ceto::mad(f)).x) << (*ceto::mad(f2)).x;
    }

