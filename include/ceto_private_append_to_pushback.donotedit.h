#pragma once

#include "ceto.h"
// unsafe;
namespace ceto {
    template <class T>struct is_vector : public std::false_type {

using std::false_type::false_type;

        };

    
template <class T, class A>
struct is_vector<std::vector<T, A>> : std::true_type {};
;
    template<class T> concept is_vector_v = (is_vector<T> :: value);
    #define CETO_PRIVATE_REAL_APPEND append
    ;
         template<class T,class Y> inline auto append_or_push_back( T &&  non_vec,  Y &&  el) -> decltype(auto) requires (!is_vector_v<T>) {
        return (*ceto::mad(std::forward<T>(non_vec))).CETO_PRIVATE_REAL_APPEND(std::forward<Y>(el));
    }

    #undef CETO_PRIVATE_REAL_APPEND
    ;
         template<class T> inline auto append_or_push_back( std::vector<T> &  vec,  auto &&  el) -> void {
        (*ceto::mad(vec)).push_back(std::forward<decltype(el)>(el));
    }


};
