
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

struct Node : ceto::shared_object {

    std::shared_ptr<Node> func;

    std::vector<std::shared_ptr<Node>> args;

    explicit Node(const std::shared_ptr<Node>&  func, const std::vector<std::shared_ptr<Node>>&  args) : func(func), args(args) {
            static_assert(std::is_reference_v<decltype(func)>);
            static_assert(std::is_const_v<std::remove_reference_t<decltype(func)>>);
            static_assert(!std::is_const_v<decltype(this -> func)>);
    }

    Node() = delete;

};

    auto main() -> int {
        std::cout << ceto::mado(ceto::mado(std::make_shared<const decltype(Node{nullptr, std::vector<std::shared_ptr<Node>>{}})>(nullptr, std::vector<std::shared_ptr<Node>>{}))->args)->size();
    }

