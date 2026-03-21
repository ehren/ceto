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
#include <map>
;
#include <unordered_map>
;
#include <ranges>
;
#include <functional>
;
#include <span>
;
#include <variant>
;
#include "ast.donotedit.h"
;
#include "visitor.donotedit.h"
;
#include "range_utility.donotedit.h"
;
// unsafe;

#if _MSC_VER
    #include <windows.h>
;
    
    #define CETO_DLSYM GetProcAddress
    #define CETO_DLOPEN LoadLibraryA
    #define CETO_DLCLOSE FreeLibrary
    ;

#else
    #include <dlfcn.h>
;
    
    #define CETO_DLSYM dlsym
    #define CETO_DLOPEN(L) dlopen(L, RTLD_NOW)
    #define CETO_DLCLOSE dlclose
    ;

#endif

struct SemanticAnalysisError : public std::runtime_error {

using std::runtime_error::runtime_error;

};

struct MacroDefinition : public ceto::shared_object, public std::enable_shared_from_this<MacroDefinition> {

    ceto::nonullpropconst<std::shared_ptr<const Node>> defmacro_node;

    ceto::nonullpropconst<std::shared_ptr<const Node>> pattern_node;

    std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>> parameters;

    std::string dll_path = {};

    std::string impl_function_name = {};

    explicit MacroDefinition(ceto::nonullpropconst<std::shared_ptr<const Node>> defmacro_node, ceto::nonullpropconst<std::shared_ptr<const Node>> pattern_node, std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>> parameters) : defmacro_node(std::move(defmacro_node)), pattern_node(std::move(pattern_node)), parameters(parameters) {}

    MacroDefinition() = delete;

};

struct MacroScope : public ceto::object {

    MacroScope const * parent = nullptr; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(nullptr), std::remove_cvref_t<decltype(parent)>>);

    std::vector<ceto::nonullpropconst<std::shared_ptr<const MacroDefinition>>> macro_definitions = std::vector<ceto::nonullpropconst<std::shared_ptr<const MacroDefinition>>>{}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<ceto::nonullpropconst<std::shared_ptr<const MacroDefinition>>>{}), std::remove_cvref_t<decltype(macro_definitions)>>);

        inline auto add_definition(const ceto::nonullpropconst<std::shared_ptr<const MacroDefinition>>&  defn) -> void {
            ceto::append_or_push_back(this -> macro_definitions, defn);
        }

        inline auto enter_scope() const -> ceto::nonullpropconst<std::unique_ptr<MacroScope>> {
            auto s = ceto::make_unique_nonullpropconst<MacroScope>();
            (*ceto::mad(s)).parent = this;
            return s;
        }

};

    inline auto is_optional_pattern(const ceto::nonullpropconst<std::shared_ptr<const Node>>&  pattern,  const std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>> &  params) -> auto {
        if (!ceto::isinstance<const Identifier>(pattern)) {
            return false;
        }
        const auto patt_param_it = (*ceto::mad(params)).find((*ceto::mad_smartptr((*ceto::mad(pattern)).name())).value());
        if (patt_param_it != (*ceto::mad(params)).end()) {
            const auto patt_param = (patt_param_it -> second);
            if (ceto::isinstance<const TypeOp>(patt_param)) {
                auto rhs { (*ceto::mad((*ceto::mad(patt_param)).args)).at(1) } ;
                auto is_alternational { false } ;
                while (const auto r = ceto::asinstance<const BitwiseOrOp>(rhs)) {                    is_alternational = true;
                    rhs = (*ceto::mad(r)).rhs();
                }
                if (is_alternational && ((*ceto::mad(rhs)).name() == "None")) {
                    return true;
                }
            }
        }
        return false;
    }

    template <typename ceto__private__T114, typename ceto__private__T215>
auto macro_matches_args(const ceto__private__T114& args, const ceto__private__T215& pattern_args,  const std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>> &  params, const decltype(false)& is_reversed = false) -> std::optional<std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>>> {
        auto pattern_iterator { (*ceto::mad(pattern_args)).begin() } ;
        auto arg_iterator { (*ceto::mad(args)).begin() } ;
        auto submatches { std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>>{} } ;
        while (true) {            if (pattern_iterator == (*ceto::mad(pattern_args)).end()) {
                if (arg_iterator != (*ceto::mad(args)).end()) {
                    return {};
                } else {
                    break;
                }
            }
            auto subpattern { (*pattern_iterator) } ;
            if (ceto::isinstance<const Identifier>(subpattern)) {
                const auto search = (*ceto::mad(params)).find((*ceto::mad_smartptr((*ceto::mad(subpattern)).name())).value());
                if (search != (*ceto::mad(params)).end()) {
                    const auto param_name = (search -> first);
                    const auto matched_param = (search -> second);
                    if (const auto type_match = ceto::asinstance<const TypeOp>(matched_param)) {
                        if (const auto list_param = ceto::asinstance<const ListLiteral>((*ceto::mad(type_match)).rhs())) {
                            if ((*ceto::mad((*ceto::mad(list_param)).args)).size() != 1) {
                                throw SemanticAnalysisError{"bad ListLiteral args in macro param"};
                            }
                            const auto wildcard_list_type = (*ceto::mad((*ceto::mad(list_param)).args)).at(0);
                            if (!ceto::isinstance<const Identifier>(wildcard_list_type)) {
                                throw SemanticAnalysisError{"bad ListLiteral arg type in macro param"};
                            }
                            const auto wildcard_list_name = (*ceto::mad(type_match)).lhs();
                            if (!ceto::isinstance<const Identifier>(wildcard_list_name)) {
                                throw SemanticAnalysisError{"arg of type ListLiteral must be an identifier"};
                            }
                            const auto wildcard_type_op = ceto::make_shared_nonullpropconst<const TypeOp>(":", std::vector<ceto::nonullpropconst<std::shared_ptr<const Node>>>{wildcard_list_name, wildcard_list_type});
                            const std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>> wildcard_list_params = {{(*ceto::mad_smartptr((*ceto::mad(wildcard_list_name)).name())).value(), wildcard_type_op}};
                            std::vector<ceto::nonullpropconst<std::shared_ptr<const Node>>> wildcard_list_matches = std::vector<ceto::nonullpropconst<std::shared_ptr<const Node>>>{}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<ceto::nonullpropconst<std::shared_ptr<const Node>>>{}), std::remove_cvref_t<decltype(wildcard_list_matches)>>);
                            while (arg_iterator != (*ceto::mad(args)).end()) {                                const auto arg = (*arg_iterator);
                                if (macro_matches(arg, wildcard_list_name, wildcard_list_params)) {
                                    (wildcard_list_matches).push_back(arg);
                                } else {
                                    break;
                                }
                                arg_iterator += 1;
                            }
                            if (is_reversed) {
                                std::reverse((*ceto::mad(wildcard_list_matches)).begin(), (*ceto::mad(wildcard_list_matches)).end());
                            }
                            (*ceto::mad(submatches)).insert_or_assign(param_name, ceto::make_shared_nonullpropconst<const ListLiteral>(wildcard_list_matches));
                            pattern_iterator += 1;
                            if (pattern_iterator == (*ceto::mad(pattern_args)).end()) {
                                if (arg_iterator != (*ceto::mad(args)).end()) {
                                    return {};
                                }
                                break;
                            }
                        }
                    }
                }
            }
            if (arg_iterator == (*ceto::mad(args)).end()) {
                while (pattern_iterator != (*ceto::mad(pattern_args)).end()) {                    if (!is_optional_pattern((*pattern_iterator), params)) {
                        return {};
                    }
                    pattern_iterator += 1;
                }
                return submatches;
            }
            const auto arg = (*arg_iterator);
            const auto m = macro_matches(arg, subpattern, params);
            if (m) {
                (*ceto::mad(submatches)).insert((*ceto::mad(m)).begin(), (*ceto::mad(m)).end());
            } else {
                if (!is_optional_pattern(subpattern, params)) {
                    return {};
                }
            }
            arg_iterator += 1;
            pattern_iterator += 1;
        }
        return submatches;
    }

    inline auto macro_matches(const ceto::nonullpropconst<std::shared_ptr<const Node>>&  node, const ceto::nonullpropconst<std::shared_ptr<const Node>>&  pattern,  const std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>> &  params) -> std::optional<std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>>> {
        if (ceto::isinstance<const Identifier>(pattern)) {
            const auto search = (*ceto::mad(params)).find((*ceto::mad_smartptr((*ceto::mad(pattern)).name())).value());
            if (search != (*ceto::mad(params)).end()) {
                const auto param_name = (search -> first);
                const auto matched_param = (search -> second);
                if (ceto::isinstance<const Identifier>(matched_param)) {
                    return std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>>{{param_name, node}};
                } else if (const auto typeop = ceto::asinstance<const TypeOp>(matched_param)) {
                    const auto param_type = (*ceto::mad(typeop)).rhs();
                    if (ceto::isinstance<const Identifier>(param_type)) {
                        if ((((*ceto::mad(param_type)).name() == "BinOp") && ceto::isinstance<const BinOp>(node)) || (((*ceto::mad(param_type)).name() == "UnOp") && ceto::isinstance<const UnOp>(node)) || ((*ceto::mad(param_type)).name() == "Node") || ((*ceto::mad(node)).classname() == (*ceto::mad((*ceto::mad(typeop)).rhs())).name())) {
                            return std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>>{{param_name, node}};
                        }
                    } else if (const auto or_type = ceto::asinstance<const BitwiseOrOp>(param_type)) {
                        const std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>> lhs_alternate_param = {{param_name, ceto::make_shared_nonullpropconst<const TypeOp>(":", std::vector {{matched_param, (*ceto::mad(or_type)).lhs()}})}};
                        if (const auto m = macro_matches(node, pattern, lhs_alternate_param)) {
                            return m;
                        }
                        const std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>> rhs_alternate_param = {{param_name, ceto::make_shared_nonullpropconst<const TypeOp>(":", std::vector {{matched_param, (*ceto::mad(or_type)).rhs()}})}};
                        if (const auto m = macro_matches(node, pattern, rhs_alternate_param)) {
                            return m;
                        }
                    }
                }
            }
        } else if (const auto binop_pattern = ceto::asinstance<const BinOp>(pattern)) {
            std::vector<ceto::nonullpropconst<std::shared_ptr<const Node>>> idents = std::vector<ceto::nonullpropconst<std::shared_ptr<const Node>>>{}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<ceto::nonullpropconst<std::shared_ptr<const Node>>>{}), std::remove_cvref_t<decltype(idents)>>);
            
                auto&& ceto__private__intermediate16 = (*ceto::mad(binop_pattern)).args;

                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate16)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size18 = std::size(ceto__private__intermediate16);
                for (size_t ceto__private__idx17 = 0; ; ceto__private__idx17++) {
                    if (std::size(ceto__private__intermediate16) != ceto__private__size18) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx17 >= ceto__private__size18) {
                        break ;
                    }
                    const auto a = ceto__private__intermediate16[ceto__private__idx17];
                                    if (ceto::isinstance<const Identifier>(a)) {
                                (idents).push_back(a);
                            }

                }
                
    
                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(idents)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size23 = std::size(idents);
                for (size_t ceto__private__idx22 = 0; ; ceto__private__idx22++) {
                    if (std::size(idents) != ceto__private__size23) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx22 >= ceto__private__size23) {
                        break ;
                    }
                    const auto i = idents[ceto__private__idx22];
                                    const auto search = (*ceto::mad(params)).find((*ceto::mad_smartptr((*ceto::mad(i)).name())).value());
                            if (search != (*ceto::mad(params)).end()) {
                                const auto param_name = (search -> first);
                                const auto typed_param = ceto::asinstance<const TypeOp>(search -> second);
                                if (!typed_param) {
                                    continue;
                                }
                                if (const auto or_param = ceto::asinstance<const BitwiseOrOp>((*ceto::mad(typed_param)).rhs())) {
                                    if (((*ceto::mad((*ceto::mad(or_param)).lhs())).name() == "None") || ((*ceto::mad((*ceto::mad(or_param)).rhs())).name() == "None")) {
                            
                                            auto&& ceto__private__intermediate19 = (*ceto::mad(binop_pattern)).args;

                                            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate19)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                                            size_t ceto__private__size21 = std::size(ceto__private__intermediate19);
                                            for (size_t ceto__private__idx20 = 0; ; ceto__private__idx20++) {
                                                if (std::size(ceto__private__intermediate19) != ceto__private__size21) {
                                                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                                                    std::terminate();
                                                }
                                                if (ceto__private__idx20 >= ceto__private__size21) {
                                                    break ;
                                                }
                                                const auto a = ceto__private__intermediate19[ceto__private__idx20];
                                                                                if ((*ceto::mad(a)).name() != (*ceto::mad(i)).name()) {
                                                                            const auto m = macro_matches(node, a, params);
                                                                            if (m) {
                                                                                return m;
                                                                            }
                                                                        }

                                            }
                                        }
                                }
                            }

                }
            }
        if ((*ceto::mad(node)).classname() != (*ceto::mad(pattern)).classname()) {
            return {};
        }
        if (((*ceto::mad(node)).func == CETO_NONE) != ((*ceto::mad(pattern)).func == CETO_NONE)) {
            return {};
        }
        if (((*ceto::mad((*ceto::mad(node)).args)).size() == 0) && ((*ceto::mad(node)).func == CETO_NONE) && ((*ceto::mad(pattern)).func == CETO_NONE)) {
            if ((*ceto::mad(node)).equals(pattern)) {
                return std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>>{};
            }
            return {};
        }
        auto submatches { std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>>{} } ;
        if ((*ceto::mad(node)).func) {
            const auto m = macro_matches((*ceto::mad_smartptr((*ceto::mad(node)).func)).value(), (*ceto::mad_smartptr((*ceto::mad(pattern)).func)).value(), params);
            if (!m) {
                return {};
            }
            (*ceto::mad(submatches)).insert((*ceto::mad(m)).begin(), (*ceto::mad(m)).end());
        }
        const auto left_to_right_matches = macro_matches_args((*ceto::mad(node)).args, (*ceto::mad(pattern)).args, params);
        if ((*ceto::mad((*ceto::mad(pattern)).args)).size() > 1) {
            const auto right_to_left_matches = macro_matches_args(ceto::util::reversed((*ceto::mad(node)).args), ceto::util::reversed((*ceto::mad(pattern)).args), params, true);
            if (right_to_left_matches && (!left_to_right_matches || ((*ceto::mad(left_to_right_matches)).size() < (*ceto::mad(right_to_left_matches)).size()))) {
                (*ceto::mad(submatches)).insert((*ceto::mad(right_to_left_matches)).begin(), (*ceto::mad(right_to_left_matches)).end());
                return submatches;
            }
        }
        if (!left_to_right_matches) {
            return {};
        }
        (*ceto::mad(submatches)).insert((*ceto::mad(left_to_right_matches)).begin(), (*ceto::mad(left_to_right_matches)).end());
        return submatches;
    }

    inline auto call_macro_impl(const ceto::nonullpropconst<std::shared_ptr<const MacroDefinition>>&  definition,  const std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>> &  match) -> ceto::nonullpropconst<std::shared_ptr<const Node>> {
        const auto handle = CETO_DLOPEN((*ceto::mad((*ceto::mad(definition)).dll_path)).c_str());
        if (!handle) {
            throw std::runtime_error("Failed to open macro dll: " + (*ceto::mad(definition)).dll_path);
        }
        const auto fptr = CETO_DLSYM(handle, (*ceto::mad((*ceto::mad(definition)).impl_function_name)).c_str());
        if (!fptr) {
            throw std::runtime_error("Failed to find symbol " + (*ceto::mad(definition)).impl_function_name + " in dll " + (*ceto::mad(definition)).dll_path);
        }
        const auto f = reinterpret_cast<decltype(+[]( const std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>> &  m, const decltype(&gensym)  gensym_ptr, const decltype(&macro_return_none)  macro_return_none_ptr, const decltype(&macro_return_skip)  macro_return_skip_ptr) -> ceto::nonullpropconst<std::shared_ptr<const Node>> {
                return macro_return_none();
                })>(fptr);
        return (*f)(match, (&gensym), (&macro_return_none), (&macro_return_skip));
    }

struct ExpandResult : public ceto::object {

    bool did_expand;

    ceto::nonullpropconst<std::shared_ptr<const Node>> _node;

    std::map<ceto::nonullpropconst<std::shared_ptr<const Node>>,std::vector<ceto::nonullpropconst<std::shared_ptr<const MacroDefinition>>>> & _skipped_definitions;

        ~ExpandResult() {
            if (this -> did_expand) {
                return;
            }
            const auto it = (*ceto::mad(this -> _skipped_definitions)).find(this -> _node);
            if (it != (*ceto::mad(this -> _skipped_definitions)).end()) {
                (*ceto::mad(it -> second)).clear();
            }
        }

    explicit ExpandResult(bool did_expand, ceto::nonullpropconst<std::shared_ptr<const Node>> _node, std::map<ceto::nonullpropconst<std::shared_ptr<const Node>>,std::vector<ceto::nonullpropconst<std::shared_ptr<const MacroDefinition>>>> & _skipped_definitions) : did_expand(did_expand), _node(std::move(_node)), _skipped_definitions(_skipped_definitions) {}

    ExpandResult() = delete;

};

struct MacroDefinitionVisitor : public BaseVisitor<MacroDefinitionVisitor> {

    std::function<void(ceto::nonullpropconst<std::shared_ptr<const MacroDefinition>>, const std::unordered_map<ceto::nonullpropconst<std::shared_ptr<const Node>>,ceto::nonullpropconst<std::shared_ptr<const Node>>> &)> on_visit_definition;

    std::optional<ceto::nonullpropconst<std::unique_ptr<MacroScope>>> current_scope = CETO_NONE; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(CETO_NONE), std::remove_cvref_t<decltype(current_scope)>>);

    std::unordered_map<ceto::nonullpropconst<std::shared_ptr<const Node>>,ceto::nonullpropconst<std::shared_ptr<const Node>>> replacements = {};

    std::map<ceto::nonullpropconst<std::shared_ptr<const Node>>,std::vector<ceto::nonullpropconst<std::shared_ptr<const MacroDefinition>>>> skipped_definitions = {};

        inline auto expand(const ceto::nonullpropconst<std::shared_ptr<const Node>>&  node) -> auto {
            auto const * scope { (&(*ceto::mad_smartptr(this -> current_scope)).value()) -> get() } ;
            while (scope) {                auto&& ceto__private__intermediate25 = scope -> macro_definitions;
auto&& ceto__private__intermediate26 = ceto::util::reversed(ceto__private__intermediate25);

for( const auto &  definition : ceto__private__intermediate26) {
                    auto skip_definition { false } ;
                    auto&& ceto__private__intermediate24 = this -> skipped_definitions;

for(  const auto & [key, defns] : ceto__private__intermediate24) {
                        if (ceto::util::contains(defns, definition)) {
                            skip_definition = true;
                            break;
                        }
                    }
                    if (skip_definition) {
                        continue;
                    }
                    const auto match = macro_matches(node, (*ceto::mad(definition)).pattern_node, (*ceto::mad(definition)).parameters);
                    if (match) {
                        const auto result = call_macro_impl(definition, (*ceto::mad_smartptr(match)).value());
                        if (result == macro_return_skip()) {
                            (*ceto::mad((*ceto::mad(this -> skipped_definitions)).at(node))).push_back(definition);
                        } else if ((result != macro_return_none())) {
                            if (result != node) {
                                (*ceto::mad(this -> replacements)).insert_or_assign(node, result);
                                (*ceto::mad(result)).accept((*this));
                                const auto did_expand = true;
                                return ExpandResult{did_expand, node, this -> skipped_definitions};
                            }
                        }
                    }
                }
                scope = (scope -> parent);
            }
            const auto did_expand = false;
            return ExpandResult{did_expand, node, this -> skipped_definitions};
        }

        inline auto visit(const Node&  n) -> void override {
            const auto node = ceto::shared_from((&n));
            const auto expand_result = this -> expand(node);
            if ((*ceto::mad(expand_result)).did_expand) {
                return;
            }
            if ((*ceto::mad(node)).func) {
                (*ceto::mad((*ceto::mad(node)).func)).accept((*this));
            }
            
                auto&& ceto__private__intermediate27 = (*ceto::mad(node)).args;

                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate27)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size29 = std::size(ceto__private__intermediate27);
                for (size_t ceto__private__idx28 = 0; ; ceto__private__idx28++) {
                    if (std::size(ceto__private__intermediate27) != ceto__private__size29) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx28 >= ceto__private__size29) {
                        break ;
                    }
                    const auto arg = ceto__private__intermediate27[ceto__private__idx28];
                                    (*ceto::mad(arg)).accept((*this));

                }
            }

        inline auto visit(const Call&  call_node) -> void override {
            const auto node = ceto::shared_from((&call_node));
            const auto expand_result = this -> expand(node);
            if ((*ceto::mad(expand_result)).did_expand) {
                return;
            }
            (*ceto::mad((*ceto::mad(node)).func)).accept((*this));
            
                auto&& ceto__private__intermediate30 = (*ceto::mad(node)).args;

                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate30)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size32 = std::size(ceto__private__intermediate30);
                for (size_t ceto__private__idx31 = 0; ; ceto__private__idx31++) {
                    if (std::size(ceto__private__intermediate30) != ceto__private__size32) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx31 >= ceto__private__size32) {
                        break ;
                    }
                    const auto arg = ceto__private__intermediate30[ceto__private__idx31];
                                    (*ceto::mad(arg)).accept((*this));

                }
                if ((*ceto::mad((*ceto::mad(node)).func)).name() != "defmacro") {
                return;
            }
            if (!ceto::isinstance<const Module>((*ceto::mad(node)).parent())) {
                return;
            }
            if ((*ceto::mad((*ceto::mad(node)).args)).size() < 2) {
                throw SemanticAnalysisError{"bad defmacro args"};
            }
            const auto pattern = ceto::bounds_check((*ceto::mad(node)).args, 0);
            if (!ceto::isinstance<const Block>((*ceto::mad((*ceto::mad(node)).args)).back())) {
                throw SemanticAnalysisError{"last defmacro arg must be a Block"};
            }
            auto parameters { std::map<std::string,ceto::nonullpropconst<std::shared_ptr<const Node>>>{} } ;
            
#if defined(__clang__) && (__clang_major__ < 16)
                const auto match_args = std::vector((*ceto::mad((*ceto::mad(node)).args)).cbegin() + 1, (*ceto::mad((*ceto::mad(node)).args)).cend() - 1);
            
#else
                const auto match_args = std::span((*ceto::mad((*ceto::mad(node)).args)).cbegin() + 1, (*ceto::mad((*ceto::mad(node)).args)).cend() - 1);
            
#endif

            
    
                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(match_args)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size34 = std::size(match_args);
                for (size_t ceto__private__idx33 = 0; ; ceto__private__idx33++) {
                    if (std::size(match_args) != ceto__private__size34) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx33 >= ceto__private__size34) {
                        break ;
                    }
                    const auto arg = match_args[ceto__private__idx33];
                                    const auto name = [&]() {if (ceto::isinstance<const Identifier>(arg)) {
                                return (*ceto::mad_smartptr((*ceto::mad(arg)).name())).value();
                            } else if (!ceto::isinstance<const TypeOp>(arg)) {
                                throw SemanticAnalysisError{"bad defmacro param type"};
                            } else if (!ceto::isinstance<const Identifier>(ceto::bounds_check((*ceto::mad(arg)).args, 0))) {
                                throw SemanticAnalysisError{"bad typed defmacro param"};
                            } else {
                                return (*ceto::mad_smartptr((*ceto::mad(ceto::bounds_check((*ceto::mad(arg)).args, 0))).name())).value();
                            }}()
            ;
                            const auto i = (*ceto::mad(parameters)).find(name);
                            if (i != (*ceto::mad(parameters)).end()) {
                                throw SemanticAnalysisError{"duplicate defmacro params"};
                            }
                            (*ceto::mad_smartptr(parameters)).emplace(name, arg);

                }
                const auto defn = ceto::make_shared_nonullpropconst<const MacroDefinition>(node, pattern, parameters);
            (*ceto::mad(this -> current_scope)).add_definition(defn);
            this -> on_visit_definition(defn, this -> replacements);
        }

        inline auto visit(const Module&  node) -> void override {
            auto s = ceto::make_unique_nonullpropconst<MacroScope>();
            (this -> current_scope) = std::move(s);
            
                auto&& ceto__private__intermediate35 = (*ceto::mad(node)).args;

                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate35)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size37 = std::size(ceto__private__intermediate35);
                for (size_t ceto__private__idx36 = 0; ; ceto__private__idx36++) {
                    if (std::size(ceto__private__intermediate35) != ceto__private__size37) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx36 >= ceto__private__size37) {
                        break ;
                    }
                    const auto arg = ceto__private__intermediate35[ceto__private__idx36];
                                    (*ceto::mad(arg)).accept((*this));

                }
            }

        inline auto visit(const Block&  block_node) -> void override {
            ceto::nonullpropconst<std::unique_ptr<MacroScope>> outer = std::move((*ceto::mad_smartptr(this -> current_scope)).value()); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::move((*ceto::mad_smartptr(this -> current_scope)).value())), std::remove_cvref_t<decltype(outer)>>);
            (this -> current_scope) = (*ceto::mad(outer)).enter_scope();
            const auto node = ceto::shared_from((&block_node));
            const auto expand_result = this -> expand(node);
            if ((*ceto::mad(expand_result)).did_expand) {
                return;
            }
            
                auto&& ceto__private__intermediate38 = (*ceto::mad(node)).args;

                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate38)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size40 = std::size(ceto__private__intermediate38);
                for (size_t ceto__private__idx39 = 0; ; ceto__private__idx39++) {
                    if (std::size(ceto__private__intermediate38) != ceto__private__size40) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx39 >= ceto__private__size40) {
                        break ;
                    }
                    const auto arg = ceto__private__intermediate38[ceto__private__idx39];
                                    (*ceto::mad(arg)).accept((*this));

                }
                (this -> current_scope) = std::move(outer);
        }

    explicit MacroDefinitionVisitor(std::function<void(ceto::nonullpropconst<std::shared_ptr<const MacroDefinition>>, const std::unordered_map<ceto::nonullpropconst<std::shared_ptr<const Node>>,ceto::nonullpropconst<std::shared_ptr<const Node>>> &)> on_visit_definition) : on_visit_definition(on_visit_definition) {}

    MacroDefinitionVisitor() = delete;

};

    inline auto expand_macros(const ceto::nonullpropconst<std::shared_ptr<const Module>>&  node, const std::function<void(ceto::nonullpropconst<std::shared_ptr<const MacroDefinition>>, const std::unordered_map<ceto::nonullpropconst<std::shared_ptr<const Node>>,ceto::nonullpropconst<std::shared_ptr<const Node>>> &)>  on_visit) -> std::unordered_map<ceto::nonullpropconst<std::shared_ptr<const Node>>,ceto::nonullpropconst<std::shared_ptr<const Node>>> {
        static_cast<void>(gensym());
        static_cast<void>(macro_return_none());
        static_cast<void>(macro_return_skip());
        auto visitor { MacroDefinitionVisitor{on_visit} } ;
        (*ceto::mad(node)).accept(visitor);
        return (*ceto::mad(visitor)).replacements;
    }

