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

class Identifier;

class ListLiteral;

struct Visitor : ceto::shared_object {

         virtual auto visit(const std::shared_ptr<const Node>&  node) -> void = 0;

         virtual auto visit(const std::shared_ptr<const Identifier>&  ident) -> void = 0;

         virtual auto visit(const std::shared_ptr<const ListLiteral>&  list_literal) -> void = 0;

};

