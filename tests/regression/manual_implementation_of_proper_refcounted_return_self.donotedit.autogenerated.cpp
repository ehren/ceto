
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


template <typename ceto__private__C1>struct A : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C1 a;

    explicit A(ceto__private__C1 a) : a(std::move(a)) {}

    A() = delete;

};

struct S : public ceto::shared_object, public std::enable_shared_from_this<S> {

        inline auto foo() const -> auto {
            return std::static_pointer_cast<std::type_identity_t<std::shared_ptr<const S>> :: element_type>(shared_from_this());
        }

        inline auto foo2() const -> std::shared_ptr<const S> {
            return std::static_pointer_cast<std::remove_reference<decltype(*this)> :: type>(shared_from_this());
            return std::static_pointer_cast<std::remove_reference<decltype(*this)> :: type>(shared_from_this());
        }

};

    auto main() -> int {
        const auto s = std::make_shared<const decltype(S())>();
        (std::cout << (&s) -> use_count()) << std::endl;
        const auto s2 = (*ceto::mad(s)).foo();
        (std::cout << (&s2) -> use_count()) << std::endl;
        const auto a = std::make_shared<const decltype(A{s})>(s);
        (std::cout << (&s2) -> use_count()) << std::endl;
        const auto s3 = (*ceto::mad((*ceto::mad(a)).a)).foo2();
        (std::cout << (&s) -> use_count()) << std::endl;
        (std::cout << (&s3) -> use_count()) << std::endl;
    }

