
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
#include "ceto_private_listcomp.donotedit.autogenerated.h"
;
#include "ceto_private_boundscheck.donotedit.autogenerated.h"
;
#include "ceto_private_convenience.donotedit.autogenerated.h"
;
#include "ceto_private_append_to_pushback.donotedit.autogenerated.h"
;
    auto main(const int  argc, const char * *  argv) -> int {
        if (const auto x = 5) {
            printf("%d", x);
        } else if ((argc == 1)) {
            printf("1");
        } else if (const auto y = 5) {
            printf("unreachable %d", y);
        } else {
            const auto z = 10;
        }
    }

