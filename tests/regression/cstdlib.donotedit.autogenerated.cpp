
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

    auto main() -> int {
        const auto fp = fopen("file.txt", "w+");
        fprintf(fp, "hello %s", "world\n");
        fclose(fp);
        const auto fp2 = fopen("file.txt", "r");
        fclose(fp2);
        const auto t = std::ifstream("file.txt");
        auto buffer { std::stringstream() } ;
        buffer << ceto::mado(t)->rdbuf();
        const auto s = ceto::mado(buffer)->str();
        (std::cout << s) << "\n";
    }

