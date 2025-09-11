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


;

;

;

;

;
namespace ceto::util {
    
    template <template <class...> class T_container>
    struct to {
    };;
     // external C++: std.ranges.range, to, T_container
;
         template<template<class...> class T_container,std::ranges::range T_range> inline auto operator|( T_range &&  r, const to<T_container>  t) -> auto {
        static_cast<void>(t);
        using value_type = typename decltype(CETO_BAN_RAW_DEREFERENCABLE((*ceto::mad(r)).begin())) :: value_type;
        return T_container<value_type>{/* unsafe: */ (*ceto::mad(r)).begin(), /* unsafe: */ (*ceto::mad(r)).end()};
    }


};

;

;

;

#define CETO_ENABLE_PRINTF_DEBUGGING
;
