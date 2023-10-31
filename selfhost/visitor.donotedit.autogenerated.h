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

struct Visitor : ceto::shared_object {

         virtual auto visit(const std::shared_ptr<const Node>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const UnOp>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const LeftAssociativeUnOp>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const BinOp>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const TypeOp>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const SyntaxTypeOp>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const AttributeAccess>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const ArrowOp>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const Assign>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const ScopeResolution>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const NamedParameter>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const Identifier>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const Call>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const ArrayAccess>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const BracedCall>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const Template>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const StringLiteral>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const IntegerLiteral>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const FloatLiteral>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const ListLike_>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const ListLiteral>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const TupleLiteral>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const BracedLiteral>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const Block>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const Module>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const RedundantParens>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const InfixWrapper_>&  node) -> void = 0;

};

