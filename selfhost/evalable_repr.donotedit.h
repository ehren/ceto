#pragma once

#include "ceto.h"
#include "ceto_private_listcomp.donotedit.h"
;
#include "ceto_private_boundscheck.donotedit.h"
;
#include "ceto_private_convenience.donotedit.h"
;
#include "ceto_private_append_to_pushback.donotedit.h"
;
#include "visitor.donotedit.h"
;
#include "ast.donotedit.h"
;
// unsafe;
struct EvalableAstReprVisitor : public BaseVisitor<EvalableAstReprVisitor> {

    bool preserve_source_loc;

    bool ceto_evalable;

    decltype(std::string {""}) repr = std::string {""};

        template <typename ceto__private__T135>
auto generate_loc(const ceto__private__T135& node) -> void {
            if (!(this -> preserve_source_loc)) {
                return;
            }
            const auto loc = (*ceto::mad((*ceto::mad(node)).source)).loc;
            (this -> repr) += ("SourceLoc(None, " + std::to_string(loc) + ")");
        }

        inline auto visit(const Node&  node) -> void override {
            (this -> repr) += ((*ceto::mad(node)).classname() + "(");
            if ((*ceto::mad(node)).func) {
                (*ceto::mad((*ceto::mad(node)).func)).accept((*this));
                (this -> repr) += ", ";
            }
            (this -> repr) += "[";
            
                auto&& ceto__private__intermediate36 = (*ceto::mad(node)).args;

                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate36)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size38 = std::size(ceto__private__intermediate36);
                for (size_t ceto__private__idx37 = 0; ; ceto__private__idx37++) {
                    if (std::size(ceto__private__intermediate36) != ceto__private__size38) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx37 >= ceto__private__size38) {
                        break ;
                    }
                    const auto arg = ceto__private__intermediate36[ceto__private__idx37];
                                    (*ceto::mad(arg)).accept((*this));
                            (this -> repr) += ", ";

                }
                (this -> repr) += (std::string {"]"} + [&]() {if (this -> ceto_evalable) {
                return ": Node";
            } else {
                return "";
            }}()
 + ", ");
            this -> generate_loc(node);
            (this -> repr) += ")";
        }

        inline auto visit(const UnOp&  node) -> void override {
            (this -> repr) += ((*ceto::mad(node)).classname() + "(\"" + (*ceto::mad(node)).op + "\", [");
            (*ceto::mad(ceto::bounds_check((*ceto::mad(node)).args, 0))).accept((*this));
            (this -> repr) += (std::string {"]"} + [&]() {if (this -> ceto_evalable) {
                return ": Node";
            } else {
                return "";
            }}()
 + ", ");
            this -> generate_loc(node);
            (this -> repr) += ")";
        }

        inline auto visit(const LeftAssociativeUnOp&  node) -> void override {
            (this -> repr) += ((*ceto::mad(node)).classname() + "(\"" + (*ceto::mad(node)).op + "\", [");
            (*ceto::mad(ceto::bounds_check((*ceto::mad(node)).args, 0))).accept((*this));
            (this -> repr) += (std::string {"]"} + [&]() {if (this -> ceto_evalable) {
                return ": Node";
            } else {
                return "";
            }}()
 + ", ");
            this -> generate_loc(node);
            (this -> repr) += ")";
        }

        inline auto visit(const BinOp&  node) -> void override {
            (this -> repr) += ((*ceto::mad(node)).classname() + "(\"" + (*ceto::mad(node)).op + "\", [");
            auto && args { (*ceto::mad(node)).args } ;
            ceto::safe_for_loop<!std::is_reference_v<decltype(args)> && ceto::OwningContainer<std::remove_cvref_t<decltype(args)>>>(args, [&](auto &&ceto__private__lambda_param39) -> ceto::LoopControl {
    const auto arg = ceto__private__lambda_param39;
                (*ceto::mad(arg)).accept((*this));
                (this -> repr) += ", ";
    return ceto::LoopControl::Continue;
});            (this -> repr) += (std::string {"]"} + [&]() {if (this -> ceto_evalable) {
                return ": Node";
            } else {
                return "";
            }}()
 + ", ");
            this -> generate_loc(node);
            (this -> repr) += ")";
        }

        inline auto visit(const Identifier&  node) -> void override {
            (this -> repr) += ((*ceto::mad(node)).classname() + "(\"" + (*ceto::mad(node)).repr() + "\"");
            (this -> repr) += ", ";
            this -> generate_loc(node);
            (this -> repr) += ")";
        }

        inline auto visit(const StringLiteral&  node) -> void override {
            (this -> repr) += ((*ceto::mad(node)).classname() + "(" + (*ceto::mad(node)).escaped() + ", ");
            if ((*ceto::mad(node)).prefix) {
                (*ceto::mad((*ceto::mad(node)).prefix)).accept((*this));
            } else {
                (this -> repr) += "None";
            }
            (this -> repr) += ", ";
            if ((*ceto::mad(node)).suffix) {
                (*ceto::mad((*ceto::mad(node)).suffix)).accept((*this));
            } else {
                (this -> repr) += "None";
            }
            (this -> repr) += ", ";
            this -> generate_loc(node);
            (this -> repr) += ")";
        }

        inline auto visit(const IntegerLiteral&  node) -> void override {
            (this -> repr) += ((*ceto::mad(node)).classname() + "(\"" + (*ceto::mad(node)).integer_string + "\", ");
            if ((*ceto::mad(node)).suffix) {
                (*ceto::mad((*ceto::mad(node)).suffix)).accept((*this));
            } else {
                (this -> repr) += "None";
            }
            (this -> repr) += ", ";
            this -> generate_loc(node);
            (this -> repr) += ")";
        }

        inline auto visit(const FloatLiteral&  node) -> void override {
            (this -> repr) += ((*ceto::mad(node)).classname() + "(\"" + (*ceto::mad(node)).float_string + "\", ");
            if ((*ceto::mad(node)).suffix) {
                (*ceto::mad((*ceto::mad(node)).suffix)).accept((*this));
            } else {
                (this -> repr) += "None";
            }
            (this -> repr) += ", ";
            this -> generate_loc(node);
            (this -> repr) += ")";
        }

    explicit EvalableAstReprVisitor(bool preserve_source_loc, bool ceto_evalable) : preserve_source_loc(preserve_source_loc), ceto_evalable(ceto_evalable) {}

    EvalableAstReprVisitor() = delete;

};

