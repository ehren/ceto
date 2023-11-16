
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


#define MFPTR_DOT(a, b) (a.*b)
#define MFPTR_ARROW(a, b) (a->*b)
;
struct Testpm : public ceto::shared_object, public std::enable_shared_from_this<Testpm> {

    int num;

        inline auto func1() const -> void {
            std::cout << "func1";
        }

    explicit Testpm(int num) : num(num) {}

    Testpm() = delete;

};

constexpr const auto pmfn = (&Testpm::func1);
constexpr const auto pmd = (&Testpm::num);
    auto main() -> int {
        const auto a_Testpm = (*std::make_shared<const decltype(Testpm{5})>(5));
        const auto p_Testpm = (&a_Testpm);
        auto a_Testpm_mut { (*std::make_shared<const decltype(Testpm{5})>(5)) } ;
        auto p_Testpm_mut { (&a_Testpm_mut) } ;
        MFPTR_DOT(a_Testpm, pmfn)();
        MFPTR_ARROW(p_Testpm, pmfn)();
        MFPTR_DOT(a_Testpm_mut, pmd) = 1;
        MFPTR_ARROW(p_Testpm_mut, pmd) = 2;
        (std::cout << MFPTR_DOT(a_Testpm, pmd)) << MFPTR_ARROW(p_Testpm, pmd);
        (std::cout << MFPTR_DOT(a_Testpm_mut, pmd)) << MFPTR_ARROW(p_Testpm_mut, pmd);
    }

