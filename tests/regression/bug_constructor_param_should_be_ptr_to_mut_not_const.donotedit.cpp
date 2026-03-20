
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

;

;

;
#include "ceto_private_listcomp.donotedit.h"
;
#include "ceto_private_boundscheck.donotedit.h"
;
#include "ceto_private_convenience.donotedit.h"
;
#include "ceto_private_append_to_pushback.donotedit.h"
;
struct Foo : public ceto::shared_object, public std::enable_shared_from_this<Foo> {

};

struct Node : public ceto::shared_object, public std::enable_shared_from_this<Node> {

    ceto::nonullpropconst<std::shared_ptr<Foo>> func;

    std::vector<ceto::nonullpropconst<std::shared_ptr<Node>>> args;

    explicit Node( ceto::nonullpropconst<std::shared_ptr<Foo>>  func, const std::vector<ceto::nonullpropconst<std::shared_ptr<Node>>>&  args) : func(func), args(args) {
            static_assert(!std::is_reference_v<decltype(func)>);
            static_assert(!std::is_const_v<std::remove_reference_t<decltype(func)>>);
            static_assert(!std::is_const_v<decltype(this -> func)>);
    }

    Node() = delete;

};

    auto main() -> int {
        const std::vector<ceto::nonullpropconst<std::shared_ptr<Node>>> arr = std::vector<ceto::nonullpropconst<std::shared_ptr<Node>>>{}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<ceto::nonullpropconst<std::shared_ptr<Node>>>{}), std::remove_cvref_t<decltype(arr)>>);
        auto foo { ceto::make_shared_nonullpropconst<Foo>() } ;
        std::cout << (*ceto::mad((*ceto::mad(ceto::make_shared_nonullpropconst<const Node>(foo, arr))).args)).size();
    }

