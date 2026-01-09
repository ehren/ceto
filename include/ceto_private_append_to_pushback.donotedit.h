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

#include "ceto_private_listcomp.donotedit.h"
;
#include "ceto_private_boundscheck.donotedit.h"
;
#include "ceto_private_convenience.donotedit.h"
;
#include "ceto_private_append_to_pushback.donotedit.h"
;
namespace ceto {
    template <class T>struct is_vector : public std::false_type {

using std::false_type::false_type;

        };

    
template <class T, class A>
struct is_vector<std::vector<T, A>> : std::true_type {};
;
    template<class T> concept is_vector_v = (is_vector<T> :: value);
         template<class T,class Y> inline auto append_or_push_back( T &&  non_vec,  Y &&  el) -> decltype(auto) requires (!is_vector_v<T>) {
        return (*ceto::mad(std::forward<T>(non_vec))).append(std::forward<Y>(el));
    }

         template<class T> inline auto append_or_push_back( std::vector<T> &  vec,  auto &&  el) -> void {
        (*ceto::mad(vec)).push_back(std::forward<decltype(el)>(el));
    }


};
