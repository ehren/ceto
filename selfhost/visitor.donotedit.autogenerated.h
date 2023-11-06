#pragma once

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

class Node;

class UnOp;

class LeftAssociativeUnOp;

class BinOp;

class TypeOp;

class SyntaxTypeOp;

class AttributeAccess;

class ArrowOp;

class ScopeResolution;

class Assign;

class NamedParameter;

class Identifier;

class Call;

class ArrayAccess;

class BracedCall;

class Template;

class StringLiteral;

class IntegerLiteral;

class FloatLiteral;

class ListLike_;

class ListLiteral;

class TupleLiteral;

class BracedLiteral;

class Block;

class Module;

class RedundantParens;

class InfixWrapper_;

struct Visitor : ceto::object {

         virtual auto visit(const Node&  node) -> void = 0;

         virtual auto visit(const UnOp&  node) -> void = 0;

         virtual auto visit(const LeftAssociativeUnOp&  node) -> void = 0;

         virtual auto visit(const BinOp&  node) -> void = 0;

         virtual auto visit(const TypeOp&  node) -> void = 0;

         virtual auto visit(const SyntaxTypeOp&  node) -> void = 0;

         virtual auto visit(const AttributeAccess&  node) -> void = 0;

         virtual auto visit(const ArrowOp&  node) -> void = 0;

         virtual auto visit(const Assign&  node) -> void = 0;

         virtual auto visit(const ScopeResolution&  node) -> void = 0;

         virtual auto visit(const NamedParameter&  node) -> void = 0;

         virtual auto visit(const Identifier&  node) -> void = 0;

         virtual auto visit(const Call&  node) -> void = 0;

         virtual auto visit(const ArrayAccess&  node) -> void = 0;

         virtual auto visit(const BracedCall&  node) -> void = 0;

         virtual auto visit(const Template&  node) -> void = 0;

         virtual auto visit(const StringLiteral&  node) -> void = 0;

         virtual auto visit(const IntegerLiteral&  node) -> void = 0;

         virtual auto visit(const FloatLiteral&  node) -> void = 0;

         virtual auto visit(const ListLike_&  node) -> void = 0;

         virtual auto visit(const ListLiteral&  node) -> void = 0;

         virtual auto visit(const TupleLiteral&  node) -> void = 0;

         virtual auto visit(const BracedLiteral&  node) -> void = 0;

         virtual auto visit(const Block&  node) -> void = 0;

         virtual auto visit(const Module&  node) -> void = 0;

         virtual auto visit(const RedundantParens&  node) -> void = 0;

         virtual auto visit(const InfixWrapper_&  node) -> void = 0;

};

template <class Derived>struct BaseVisitor : public Visitor {

using Visitor::Visitor;

         virtual inline auto visit(const Node&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const UnOp&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const LeftAssociativeUnOp&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const BinOp&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const TypeOp&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const SyntaxTypeOp&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const AttributeAccess&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const ArrowOp&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const Assign&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const ScopeResolution&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const NamedParameter&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const Identifier&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const Call&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const ArrayAccess&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const BracedCall&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const Template&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const StringLiteral&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const IntegerLiteral&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const FloatLiteral&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const ListLike_&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const ListLiteral&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const TupleLiteral&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const BracedLiteral&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const Block&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const Module&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const RedundantParens&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

         virtual inline auto visit(const InfixWrapper_&  node) -> void {
            static_cast<Derived *>(this) -> visit(node);
        }

};

