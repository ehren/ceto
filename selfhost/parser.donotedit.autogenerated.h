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


#include "ceto.h"
//#include "ceto_private_boundscheck.donotedit.autogenerated.h"

#include "ceto_private_listcomp.donotedit.autogenerated.h"
;
#include "ceto_private_boundscheck.donotedit.autogenerated.h"
;
#include "ceto_private_convenience.donotedit.autogenerated.h"
;
#include "ceto_private_append_to_pushback.donotedit.autogenerated.h"
;
#include <peglib.h>
;
#include <iostream>
;
#include "ast.donotedit.autogenerated.h"
;
    inline auto parse_test(const std::string&  grammar_path, const std::string&  str) -> void {
        const auto grammar_file = std::ifstream(grammar_path);
        auto grammar_buffer { std::stringstream() } ;
        grammar_buffer << (*ceto::mad(grammar_file)).rdbuf();
        const auto grammar_string = (*ceto::mad(grammar_buffer)).str();
        auto parser { peg::parser() } ;
        const auto ok = (*ceto::mad(parser)).load_grammar((*ceto::mad(grammar_string)).c_str());
        if (!ok) {
            throw std::runtime_error("failed to load grammar");
        }
        (*ceto::mad(parser)).parse(str);
    }

