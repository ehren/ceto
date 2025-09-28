
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
struct Node;

struct Identifier;

struct BinOp;

struct Add;

struct Visitor : public ceto::shared_object, public std::enable_shared_from_this<Visitor> {

         virtual auto visit(const ceto::propagate_const<std::shared_ptr<const Node>>&  node) -> void = 0;

         virtual auto visit(const ceto::propagate_const<std::shared_ptr<const Identifier>>&  node) -> void = 0;

         virtual auto visit(const ceto::propagate_const<std::shared_ptr<const BinOp>>&  node) -> void = 0;

         virtual auto visit(const ceto::propagate_const<std::shared_ptr<const Add>>&  node) -> void = 0;

         virtual ~Visitor() = default;

};

struct Node : public ceto::shared_object, public std::enable_shared_from_this<Node> {

    int loc;

         virtual inline auto accept( ceto::propagate_const<std::shared_ptr<Visitor>>  visitor) const -> void {
            const auto self = ceto::shared_from(this);
            (*ceto::mad(visitor)).visit(self);
        }

         virtual ~Node() = default;

    explicit Node(int loc) : loc(loc) {}

    Node() = delete;

};

struct Identifier : public Node {

    std::string name;

         virtual inline auto accept( ceto::propagate_const<std::shared_ptr<Visitor>>  visitor) const -> void {
            const auto self = ceto::shared_from(this);
            (*ceto::mad(visitor)).visit(self);
        }

    explicit Identifier(const std::string&  name, const decltype(0)& loc = 0) : Node (loc), name(name) {
    }

    Identifier() = delete;

};

struct BinOp : public Node {

    std::vector<ceto::propagate_const<std::shared_ptr<const Node>>> args;

         virtual inline auto accept( ceto::propagate_const<std::shared_ptr<Visitor>>  visitor) const -> void {
            const auto self = ceto::shared_from(this);
            (*ceto::mad(visitor)).visit(self);
        }

    explicit BinOp(const std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>&  args, const decltype(0)& loc = 0) : Node (loc), args(args) {
    }

    BinOp() = delete;

};

struct Add : public BinOp {

using BinOp::BinOp;

         virtual inline auto accept( ceto::propagate_const<std::shared_ptr<Visitor>>  visitor) const -> void {
            const auto self = ceto::shared_from(this);
            (*ceto::mad(visitor)).visit(self);
        }

};

struct SimpleVisitor : public Visitor {

using Visitor::Visitor;

    decltype(std::string {""}) record = std::string {""};

         virtual inline auto visit(const ceto::propagate_const<std::shared_ptr<const Node>>&  node) -> void {
            (this -> record) += "visiting Node\n";
        }

         virtual inline auto visit(const ceto::propagate_const<std::shared_ptr<const Identifier>>&  ident) -> void {
            (this -> record) += ("visiting Identifier " + (*ceto::mad(ident)).name + "\n");
        }

         virtual inline auto visit(const ceto::propagate_const<std::shared_ptr<const BinOp>>&  node) -> void {
            const auto self = ceto::shared_from(this);
            (this -> record) += "visiting BinOp\n";
            
                auto&& ceto__private__intermediate1 = (*ceto::mad(node)).args;

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
                    const auto arg = ceto__private__intermediate1[ceto__private__idx2];
                                    (*ceto::mad(arg)).accept(self);

                }
            }

         virtual inline auto visit(const ceto::propagate_const<std::shared_ptr<const Add>>&  node) -> void {
            const auto self = ceto::shared_from(this);
            (this -> record) += "visiting Add\n";
            
                auto&& ceto__private__intermediate4 = (*ceto::mad(node)).args;

                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate4)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size6 = std::size(ceto__private__intermediate4);
                for (size_t ceto__private__idx5 = 0; ; ceto__private__idx5++) {
                    if (std::size(ceto__private__intermediate4) != ceto__private__size6) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx5 >= ceto__private__size6) {
                        break ;
                    }
                    const auto arg = ceto__private__intermediate4[ceto__private__idx5];
                                    (*ceto::mad(arg)).accept(self);

                }
            }

};

    auto main() -> int {
        const auto node = ceto::make_shared_propagate_const<const Node>(0);
        const auto ident = ceto::make_shared_propagate_const<const Identifier>("a", 5);
        const std::vector<ceto::propagate_const<std::shared_ptr<const Node>>> args = std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>{ident, node, ident}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>{ident, node, ident}), std::remove_cvref_t<decltype(args)>>);
        const ceto::propagate_const<std::shared_ptr<const Add>> add = ceto::make_shared_propagate_const<const Add>(args); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(ceto::make_shared_propagate_const<const Add>(args)), std::remove_cvref_t<decltype(add)>>);
        auto simple_visitor { ceto::make_shared_propagate_const<SimpleVisitor>() } ;
        (*ceto::mad(ident)).accept(simple_visitor);
        (*ceto::mad(add)).accept(simple_visitor);
        std::cout << (*ceto::mad(simple_visitor)).record;
    }

