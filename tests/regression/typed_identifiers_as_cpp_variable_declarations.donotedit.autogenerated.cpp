
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
    auto main() -> int {
         int x;
        x = 0;
        static_cast<void>(x);
        const auto f = []( const char *  y,  int  z) {
                using namespace std;
                typedef int t;
                const t w { 3 } ; static_assert(std::is_convertible_v<decltype(3), decltype(w)>);
                (((cout << y) << z) << w) << endl;
                z = 2;
                (cout << z) << endl;
                return void();
                };
        f("hi", 5);
    }

