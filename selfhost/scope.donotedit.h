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
#include "ast.donotedit.h"
;
#include "utility.donotedit.h"
;
// unsafe;
struct ClassDefinition : public ceto::shared_object, public std::enable_shared_from_this<ClassDefinition> {

    ceto::propagate_const<std::shared_ptr<const Identifier>> name_node;

    ceto::propagate_const<std::shared_ptr<const Call>> class_def_node;

    bool is_unique;

    bool is_struct;

    bool is_forward_declaration;

    decltype(false) is_pure_virtual = false;

    decltype(false) is_concrete = false;

        inline auto repr() const -> auto {
            return (this -> class_name() + "(" + (*ceto::mad(this -> name_node)).repr() + ", " + (*ceto::mad(this -> class_def_node)).repr() + std::to_string(this -> is_unique) + ", " + std::to_string(this -> is_struct) + ", " + std::to_string(this -> is_forward_declaration) + ")");
        }

         virtual inline auto class_name() const -> std::string {
            return ceto::util::typeid_name((*this));
        }

         virtual ~ClassDefinition() = default;

    explicit ClassDefinition(ceto::propagate_const<std::shared_ptr<const Identifier>> name_node, ceto::propagate_const<std::shared_ptr<const Call>> class_def_node, bool is_unique, bool is_struct, bool is_forward_declaration) : name_node(std::move(name_node)), class_def_node(std::move(class_def_node)), is_unique(is_unique), is_struct(is_struct), is_forward_declaration(is_forward_declaration) {}

    ClassDefinition() = delete;

};

struct InterfaceDefinition : public ClassDefinition {

    explicit InterfaceDefinition() : ClassDefinition (nullptr, nullptr, false, false, false) {
    }

};

struct FunctionDefinition : public ceto::shared_object, public std::enable_shared_from_this<FunctionDefinition> {

    ceto::propagate_const<std::shared_ptr<const Node>> def_node;

    ceto::propagate_const<std::shared_ptr<const Identifier>> function_name;

         virtual inline auto class_name() const -> std::string {
            return ceto::util::typeid_name((*this));
        }

        inline auto repr() const -> auto {
            return (this -> class_name() + "(" + (*ceto::mad(this -> def_node)).repr() + ", " + (*ceto::mad(this -> function_name)).repr() + ")");
        }

         virtual ~FunctionDefinition() = default;

    explicit FunctionDefinition(ceto::propagate_const<std::shared_ptr<const Node>> def_node, ceto::propagate_const<std::shared_ptr<const Identifier>> function_name) : def_node(std::move(def_node)), function_name(std::move(function_name)) {}

    FunctionDefinition() = delete;

};

struct NamespaceDefinition : public ceto::shared_object, public std::enable_shared_from_this<NamespaceDefinition> {

    ceto::propagate_const<std::shared_ptr<const Call>> namespace_node;

    ceto::propagate_const<std::shared_ptr<const Node>> namespace_name;

         virtual inline auto class_name() const -> std::string {
            return ceto::util::typeid_name((*this));
        }

        inline auto repr() const -> auto {
            return (this -> class_name() + "(" + (*ceto::mad(this -> namespace_node)).repr() + ", " + (*ceto::mad(this -> namespace_name)).repr() + ")");
        }

         virtual ~NamespaceDefinition() = default;

    explicit NamespaceDefinition(ceto::propagate_const<std::shared_ptr<const Call>> namespace_node, ceto::propagate_const<std::shared_ptr<const Node>> namespace_name) : namespace_node(std::move(namespace_node)), namespace_name(std::move(namespace_name)) {}

    NamespaceDefinition() = delete;

};

struct VariableDefinition : public ceto::shared_object, public std::enable_shared_from_this<VariableDefinition> {

    ceto::propagate_const<std::shared_ptr<const Identifier>> defined_node;

    ceto::propagate_const<std::shared_ptr<const Node>> defining_node;

         virtual inline auto class_name() const -> std::string {
            return ceto::util::typeid_name((*this));
        }

        inline auto repr() const -> auto {
            return (this -> class_name() + "(" + (*ceto::mad(this -> defined_node)).repr() + ", " + (*ceto::mad(this -> defining_node)).repr() + ")");
        }

         virtual ~VariableDefinition() = default;

    explicit VariableDefinition(ceto::propagate_const<std::shared_ptr<const Identifier>> defined_node, ceto::propagate_const<std::shared_ptr<const Node>> defining_node) : defined_node(std::move(defined_node)), defining_node(std::move(defining_node)) {}

    VariableDefinition() = delete;

};

struct LocalVariableDefinition : public VariableDefinition {

using VariableDefinition::VariableDefinition;

};

struct GlobalVariableDefinition : public VariableDefinition {

using VariableDefinition::VariableDefinition;

};

struct FieldDefinition : public VariableDefinition {

using VariableDefinition::VariableDefinition;

};

struct ParameterDefinition : public VariableDefinition {

using VariableDefinition::VariableDefinition;

};

    inline auto creates_new_variable_scope(const ceto::propagate_const<std::shared_ptr<const Node>>&  e) -> auto {
        if ((std::dynamic_pointer_cast<const Call>(ceto::get_underlying(e)) != nullptr)) {
            const auto name = (*ceto::mad((*ceto::mad(e)).func)).name();
            if (name) {
                return ceto::util::contains(std::vector {{std::string {"def"}, std::string {"lambda"}, std::string {"class"}, std::string {"struct"}, std::string {"defmacro"}}}, (*ceto::mad_smartptr(name)).value());
            } else if (((std::dynamic_pointer_cast<const ArrayAccess>(ceto::get_underlying((*ceto::mad(e)).func)) != nullptr) && ((*ceto::mad((*ceto::mad((*ceto::mad(e)).func)).func)).name() == "lambda"))) {
                return true;
            }
        }
        return false;
    }

    inline auto comes_before(const ceto::propagate_const<std::shared_ptr<const Node>>&  root, const ceto::propagate_const<std::shared_ptr<const Node>>&  before, const ceto::propagate_const<std::shared_ptr<const Node>>&  after) -> std::optional<bool> {
        if (root == before) {
            return true;
        } else if ((root == after)) {
            return false;
        }
        
            auto&& ceto__private__intermediate14 = (*ceto::mad(root)).args;

            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate14)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size16 = std::size(ceto__private__intermediate14);
            for (size_t ceto__private__idx15 = 0; ; ceto__private__idx15++) {
                if (std::size(ceto__private__intermediate14) != ceto__private__size16) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx15 >= ceto__private__size16) {
                    break ;
                }
                const auto arg = ceto__private__intermediate14[ceto__private__idx15];
                            const auto cb = comes_before(arg, before, after);
                    if ((*ceto::mad_smartptr(cb)).has_value()) {
                        return cb;
                    }

            }
            if ((*ceto::mad(root)).func) {
            const auto cb = comes_before((*ceto::mad(root)).func, before, after);
            if ((*ceto::mad_smartptr(cb)).has_value()) {
                return cb;
            }
        }
        return {};
    }

struct Scope : public ceto::shared_object, public std::enable_shared_from_this<Scope> {

    decltype(std::map<std::string,std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>>()) interfaces = std::map<std::string,std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>>();

    std::vector<ceto::propagate_const<std::shared_ptr<const ClassDefinition>>> class_definitions = std::vector<ceto::propagate_const<std::shared_ptr<const ClassDefinition>>>{}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<ceto::propagate_const<std::shared_ptr<const ClassDefinition>>>{}), std::remove_cvref_t<decltype(class_definitions)>>);

    std::vector<ceto::propagate_const<std::shared_ptr<const VariableDefinition>>> variable_definitions = std::vector<ceto::propagate_const<std::shared_ptr<const VariableDefinition>>>{}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<ceto::propagate_const<std::shared_ptr<const VariableDefinition>>>{}), std::remove_cvref_t<decltype(variable_definitions)>>);

    std::vector<ceto::propagate_const<std::shared_ptr<const FunctionDefinition>>> function_definitions = std::vector<ceto::propagate_const<std::shared_ptr<const FunctionDefinition>>>{}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<ceto::propagate_const<std::shared_ptr<const FunctionDefinition>>>{}), std::remove_cvref_t<decltype(function_definitions)>>);

    std::vector<ceto::propagate_const<std::shared_ptr<const NamespaceDefinition>>> namespace_definitions = std::vector<ceto::propagate_const<std::shared_ptr<const NamespaceDefinition>>>{}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<ceto::propagate_const<std::shared_ptr<const NamespaceDefinition>>>{}), std::remove_cvref_t<decltype(namespace_definitions)>>);

    std::vector<ceto::propagate_const<std::shared_ptr<const Node>>> unsafe_nodes = std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>{}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>{}), std::remove_cvref_t<decltype(unsafe_nodes)>>);

    std::vector<ceto::propagate_const<std::shared_ptr<const Node>>> external_cpp = std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>{}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<ceto::propagate_const<std::shared_ptr<const Node>>>{}), std::remove_cvref_t<decltype(external_cpp)>>);

    decltype(0) indent = 0;

    std::weak_ptr<const Scope> _parent = {};

    decltype(false) in_function_body = false;

    decltype(false) in_function_param_list = false;

    decltype(false) in_class_body = false;

    decltype(false) in_decltype = false;

    decltype(false) _is_unsafe = false;

        inline auto indent_str() const -> auto {
            return std::string(4 * (this -> indent), ' ');
        }

        inline auto add_variable_definition(const ceto::propagate_const<std::shared_ptr<const Identifier>>&  defined_node, const ceto::propagate_const<std::shared_ptr<const Node>>&  defining_node) -> void {
            auto parent { (*ceto::mad(defined_node)).parent() } ;
            while (parent) {                if (creates_new_variable_scope(parent)) {
                    const auto name = (*ceto::mad((*ceto::mad(parent)).func)).name();
                    if ((name == "class") || (name == "struct")) {
                        const auto defn = ceto::make_shared_propagate_const<const FieldDefinition>(defined_node, defining_node);
                        ceto::append_or_push_back(this -> variable_definitions, defn);
                    } else if (((name == "def") || (name == "lambda") || (name == "defmacro"))) {
                        const auto defn = ceto::make_shared_propagate_const<const ParameterDefinition>(defined_node, defining_node);
                        ceto::append_or_push_back(this -> variable_definitions, defn);
                    } else {
                        const auto defn = ceto::make_shared_propagate_const<const LocalVariableDefinition>(defined_node, defining_node);
                        ceto::append_or_push_back(this -> variable_definitions, defn);
                        std::cerr << "this is no good?\n";
                    }
                    return;
                } else if (((std::dynamic_pointer_cast<const Block>(ceto::get_underlying(parent)) != nullptr) && creates_new_variable_scope((*ceto::mad(parent)).parent()))) {
                    const auto name = (*ceto::mad((*ceto::mad((*ceto::mad(parent)).parent())).func)).name();
                    if ((name == "class") || (name == "struct")) {
                        const auto defn = ceto::make_shared_propagate_const<const FieldDefinition>(defined_node, defining_node);
                        ceto::append_or_push_back(this -> variable_definitions, defn);
                    } else {
                        const auto defn = ceto::make_shared_propagate_const<const LocalVariableDefinition>(defined_node, defining_node);
                        ceto::append_or_push_back(this -> variable_definitions, defn);
                    }
                    return;
                }
                parent = (*ceto::mad(parent)).parent();
            }
            const auto defn = ceto::make_shared_propagate_const<const GlobalVariableDefinition>(defined_node, defining_node);
            ceto::append_or_push_back(this -> variable_definitions, defn);
        }

        inline auto add_interface_method(const std::string&  interface_name, const ceto::propagate_const<std::shared_ptr<const Node>>&  interface_method_def_node) -> void {
            ceto::append_or_push_back(ceto::bounds_check(this -> interfaces, interface_name), interface_method_def_node);
        }

        inline auto add_class_definition(const ceto::propagate_const<std::shared_ptr<const ClassDefinition>>&  class_definition) -> void {
            ceto::append_or_push_back(this -> class_definitions, class_definition);
        }

        inline auto add_function_definition(const ceto::propagate_const<std::shared_ptr<const FunctionDefinition>>&  function_definition) -> void {
            ceto::append_or_push_back(this -> function_definitions, function_definition);
        }

        inline auto add_namespace_definition(const ceto::propagate_const<std::shared_ptr<const NamespaceDefinition>>&  namespace_definition) -> void {
            ceto::append_or_push_back(this -> namespace_definitions, namespace_definition);
        }

        inline auto lookup_class(const ceto::propagate_const<std::shared_ptr<const Node>>&  class_node) const -> ceto::propagate_const<std::shared_ptr<const ClassDefinition>> {
            if (!(std::dynamic_pointer_cast<const Identifier>(ceto::get_underlying(class_node)) != nullptr)) {
                return nullptr;
            }
            
                auto&& ceto__private__intermediate17 = this -> class_definitions;

                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate17)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size19 = std::size(ceto__private__intermediate17);
                for (size_t ceto__private__idx18 = 0; ; ceto__private__idx18++) {
                    if (std::size(ceto__private__intermediate17) != ceto__private__size19) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx18 >= ceto__private__size19) {
                        break ;
                    }
                    const auto c = ceto__private__intermediate17[ceto__private__idx18];
                                    if ((*ceto::mad((*ceto::mad(c)).name_node)).name() == (*ceto::mad(class_node)).name()) {
                                return c;
                            }

                }
                if ((*ceto::mad(this -> interfaces)).contains((*ceto::mad_smartptr((*ceto::mad(class_node)).name())).value())) {
                return ceto::make_shared_propagate_const<const InterfaceDefinition>();
            }
            if (const auto s = (*ceto::mad(this -> _parent)).lock()) {
                return (*ceto::mad(s)).lookup_class(class_node);
            }
            return nullptr;
        }

        inline auto lookup_function(const ceto::propagate_const<std::shared_ptr<const Node>>&  function_name_node) const -> ceto::propagate_const<std::shared_ptr<const FunctionDefinition>> {
            if (!(std::dynamic_pointer_cast<const Identifier>(ceto::get_underlying(function_name_node)) != nullptr)) {
                return nullptr;
            }
            
                auto&& ceto__private__intermediate20 = this -> function_definitions;

                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate20)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size22 = std::size(ceto__private__intermediate20);
                for (size_t ceto__private__idx21 = 0; ; ceto__private__idx21++) {
                    if (std::size(ceto__private__intermediate20) != ceto__private__size22) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx21 >= ceto__private__size22) {
                        break ;
                    }
                    const auto f = ceto__private__intermediate20[ceto__private__idx21];
                                    if ((*ceto::mad((*ceto::mad(f)).function_name)).name() == (*ceto::mad(function_name_node)).name()) {
                                return f;
                            }

                }
                if (const auto s = (*ceto::mad(this -> _parent)).lock()) {
                return (*ceto::mad(s)).lookup_function(function_name_node);
            }
            return nullptr;
        }

        inline auto lookup_namespace(const ceto::propagate_const<std::shared_ptr<const Node>>&  namespace_name_node) const -> ceto::propagate_const<std::shared_ptr<const NamespaceDefinition>> {
            
                auto&& ceto__private__intermediate23 = this -> namespace_definitions;

                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate23)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size25 = std::size(ceto__private__intermediate23);
                for (size_t ceto__private__idx24 = 0; ; ceto__private__idx24++) {
                    if (std::size(ceto__private__intermediate23) != ceto__private__size25) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx24 >= ceto__private__size25) {
                        break ;
                    }
                    const auto n = ceto__private__intermediate23[ceto__private__idx24];
                                    if ((*ceto::mad((*ceto::mad(n)).namespace_name)).equals(namespace_name_node)) {
                                return n;
                            }

                }
                if (const auto s = (*ceto::mad(this -> _parent)).lock()) {
                return (*ceto::mad(s)).lookup_namespace(namespace_name_node);
            }
            return nullptr;
        }

        inline auto is_node_unsafe(const ceto::propagate_const<std::shared_ptr<const Node>>&  node) const -> auto {
            
                auto&& ceto__private__intermediate26 = this -> unsafe_nodes;

                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate26)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size28 = std::size(ceto__private__intermediate26);
                for (size_t ceto__private__idx27 = 0; ; ceto__private__idx27++) {
                    if (std::size(ceto__private__intermediate26) != ceto__private__size28) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx27 >= ceto__private__size28) {
                        break ;
                    }
                    const auto x = ceto__private__intermediate26[ceto__private__idx27];
                                    if ((*ceto::mad(x)).equals(node)) {
                                return true;
                            }

                }
                const auto parent = (*ceto::mad(this -> _parent)).lock();
            return (parent && (*ceto::mad(parent)).is_node_unsafe(node));
        }

        inline auto mark_node_unsafe(const ceto::propagate_const<std::shared_ptr<const Node>>&  node) -> void {
            ceto::append_or_push_back(this -> unsafe_nodes, node);
        }

        inline auto is_external_cpp(const ceto::propagate_const<std::shared_ptr<const Node>>&  node) const -> auto {
            
                auto&& ceto__private__intermediate29 = this -> external_cpp;

                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate29)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size31 = std::size(ceto__private__intermediate29);
                for (size_t ceto__private__idx30 = 0; ; ceto__private__idx30++) {
                    if (std::size(ceto__private__intermediate29) != ceto__private__size31) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx30 >= ceto__private__size31) {
                        break ;
                    }
                    const auto x = ceto__private__intermediate29[ceto__private__idx30];
                                    if ((*ceto::mad(x)).equals(node)) {
                                return true;
                            }

                }
                const auto parent = (*ceto::mad(this -> _parent)).lock();
            return (parent && (*ceto::mad(parent)).is_external_cpp(node));
        }

        inline auto add_external_cpp(const ceto::propagate_const<std::shared_ptr<const Node>>&  node) -> void {
            ceto::append_or_push_back(this -> external_cpp, node);
        }

        inline auto find_defs(const ceto::propagate_const<std::shared_ptr<const Node>>&  var_node, const decltype(true)& find_all = true) const -> std::vector<ceto::propagate_const<std::shared_ptr<const VariableDefinition>>> {
            if (!(std::dynamic_pointer_cast<const Identifier>(ceto::get_underlying(var_node)) != nullptr)) {
                return {};
            }
            std::vector<ceto::propagate_const<std::shared_ptr<const VariableDefinition>>> results = std::vector<ceto::propagate_const<std::shared_ptr<const VariableDefinition>>>{}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<ceto::propagate_const<std::shared_ptr<const VariableDefinition>>>{}), std::remove_cvref_t<decltype(results)>>);
            
                auto&& ceto__private__intermediate32 = this -> variable_definitions;

                static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate32)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                size_t ceto__private__size34 = std::size(ceto__private__intermediate32);
                for (size_t ceto__private__idx33 = 0; ; ceto__private__idx33++) {
                    if (std::size(ceto__private__intermediate32) != ceto__private__size34) {
                        std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                        std::terminate();
                    }
                    if (ceto__private__idx33 >= ceto__private__size34) {
                        break ;
                    }
                    const auto d = ceto__private__intermediate32[ceto__private__idx33];
                                    if (((*ceto::mad((*ceto::mad(d)).defined_node)).name() == (*ceto::mad(var_node)).name()) && ((*ceto::mad(d)).defined_node != var_node)) {
                                auto parent_block { (*ceto::mad((*ceto::mad(d)).defined_node)).parent() } ;
                                while (true) {                        if ((std::dynamic_pointer_cast<const Module>(ceto::get_underlying(parent_block)) != nullptr)) {
                                        break;
                                    }
                                    parent_block = (*ceto::mad(parent_block)).parent();
                                }
                                const auto defined_before = comes_before(parent_block, (*ceto::mad(d)).defined_node, var_node);
                                if (defined_before && (*ceto::mad_smartptr(defined_before)).value()) {
                                    if (!find_all) {
                                        return std::vector {d};
                                    }
                                    (results).push_back(d);
                                    if (const auto assign = ceto::propagate_const<std::shared_ptr<const Assign>>(std::dynamic_pointer_cast<const Assign>(ceto::get_underlying((*ceto::mad(d)).defining_node)))) {
                                        if (const auto ident = ceto::propagate_const<std::shared_ptr<const Identifier>>(std::dynamic_pointer_cast<const Identifier>(ceto::get_underlying((*ceto::mad(assign)).rhs())))) {
                                            const auto more = this -> find_defs(ident, find_all);
                                            (*ceto::mad(results)).insert((*ceto::mad(results)).end(), (*ceto::mad(more)).begin(), (*ceto::mad(more)).end());
                                        }
                                    }
                                }
                            }

                }
                if (const auto s = (*ceto::mad(this -> _parent)).lock()) {
                const auto more = (*ceto::mad(s)).find_defs(var_node, find_all);
                (*ceto::mad(results)).insert((*ceto::mad(results)).end(), (*ceto::mad(more)).begin(), (*ceto::mad(more)).end());
            }
            return results;
        }

        inline auto find_def(const ceto::propagate_const<std::shared_ptr<const Node>>&  var_node) const -> auto {
            const auto find_all = false;
            const auto found = this -> find_defs(var_node, find_all);
            return [&]() {if ((*ceto::mad(found)).size() > 0) {
                return ceto::bounds_check(found, 0);
            } else {
                const ceto::propagate_const<std::shared_ptr<const VariableDefinition>> none_result = nullptr; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(nullptr), std::remove_cvref_t<decltype(none_result)>>);
                return none_result;
            }}()
;
        }

        inline auto enter_scope() const -> ceto::propagate_const<std::shared_ptr<const Scope>> {
            const auto self = ceto::shared_from(this);
            auto s { ceto::make_shared_propagate_const<Scope>() } ;
            (*ceto::mad(s))._parent = ceto::get_underlying(self);
            (*ceto::mad(s)).in_function_body = (this -> in_function_body);
            (*ceto::mad(s)).in_decltype = (this -> in_decltype);
            (*ceto::mad(s))._is_unsafe = (this -> _is_unsafe);
            (*ceto::mad(s)).external_cpp = (this -> external_cpp);
            (*ceto::mad(s)).namespace_definitions = (this -> namespace_definitions);
            (*ceto::mad(s)).indent = ((this -> indent) + 1);
            return s;
        }

        inline auto parent() const -> auto {
            return (*ceto::mad(this -> _parent)).lock();
        }

        inline auto is_unsafe() const -> bool {
            return ((this -> _is_unsafe) || (this -> parent() && (*ceto::mad(this -> parent())).is_unsafe()));
        }

        inline auto set_is_unsafe(const bool  u) -> void {
            (this -> _is_unsafe) = u;
        }

};

