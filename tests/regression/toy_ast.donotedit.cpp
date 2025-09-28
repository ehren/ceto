
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
struct Node : public ceto::shared_object, public std::enable_shared_from_this<Node> {

    ceto::propagate_const<std::shared_ptr<const Node>> func;

    std::vector<ceto::propagate_const<std::shared_ptr<const Node>>> args;

         virtual inline auto repr() const -> std::string {
            auto r { (std::string {"generic node with func "} + [&]() {if (this -> func) {
                return (*ceto::mad(this -> func)).repr();
            } else {
                return std::string {"none"};
            }}()
 + "(" + std::to_string([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype((*ceto::mad(this -> args)).size())> ) && true)  || true )); return (*ceto::mad(this -> args)).size(); }()) + " args.)\n") } ;
            
                auto&& ceto__private__intermediate1 = this -> args;

                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate1)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size3 = std::size(ceto__private__intermediate1);
                for (size_t ceto__private__idx2 = 0; ; ceto__private__idx2++) {
                    if (std::size(ceto__private__intermediate1) != ceto__private__size3) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx2 >= ceto__private__size3) {
                        break ;
                    }
                    const auto a = ceto__private__intermediate1[ceto__private__idx2];
                                    r = (r + "arg: " + (*ceto::mad(a)).repr());

                }
                return r;
        }

         virtual ~Node() = default;

    explicit Node(ceto::propagate_const<std::shared_ptr<const Node>> func, std::vector<ceto::propagate_const<std::shared_ptr<const Node>>> args) : func(std::move(func)), args(std::move(args)) {}

    Node() = delete;

};

struct Identifier : public Node {

    std::string name;

        inline auto repr() const -> std::string {
            return (std::string {"identifier node with name: "} + (this -> name) + "\n");
        }

    explicit Identifier(const std::string&  name) : Node (nullptr, std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>{}), name(name) {
    }

    Identifier() = delete;

};

    auto main() -> int {
         // unsafe external C++: static_pointer_cast, ceto.get_underlying
;
        const auto id = ceto::make_shared_propagate_const<const Identifier>("a");
        std::cout << (*ceto::mad(id)).name;
        const ceto::propagate_const<std::shared_ptr<const Node>> id_node = ceto::make_shared_propagate_const<const Identifier>("a"); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(ceto::make_shared_propagate_const<const Identifier>("a")), std::remove_cvref_t<decltype(id_node)>>);
        std::cout << (*ceto::mad(static_pointer_cast<std::type_identity_t<ceto::propagate_const<std::shared_ptr<const Identifier>>> :: element_type>(ceto::get_underlying(id_node)))).name;
        std::cout << (*ceto::mad(ceto::propagate_const<std::shared_ptr<const Identifier>>(std::dynamic_pointer_cast<const Identifier>(ceto::get_underlying(id_node))))).name;
        const std::vector<ceto::propagate_const<std::shared_ptr<const Node>>> args = std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>{id, id_node}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>{id, id_node}), std::remove_cvref_t<decltype(args)>>);
        const auto args2 = std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>{id, id_node};
        static_cast<void>(args2);
        const auto node = ceto::make_shared_propagate_const<const Node>(id, args);
        std::cout << (ceto::bounds_check((*ceto::mad(node)).args, 0) == nullptr);
        std::cout << "\n" << (*ceto::mad(node)).repr();
        std::cout << (*ceto::mad(ceto::bounds_check((*ceto::mad(node)).args, 0))).repr();
    }

