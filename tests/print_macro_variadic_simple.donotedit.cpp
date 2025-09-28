
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
#include <fstream>
;

;
    auto main() -> int {
        auto a { "a" } ;
        std::cout << std::endl;
        std::cout << a << std::endl;
        std::cout << a << a << std::endl;
        std::cerr << "🙀" << a << a << std::endl;
         // unsafe external C++: std.ofstream
;
        std::ofstream("example.txt") << a << std::endl;
        std::cerr << "🙀" << a << std::endl;
        std::cout << std::endl;
        std::cerr << "🙀" << "aa\n";
        std::cerr << "🙀" << "aa\n\n";
        std::cerr << "🙀" << a << std::endl;
    }

