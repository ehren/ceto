#ifndef CETO_DETAIL_SP_FORWARD_HPP_INCLUDED
#define CETO_DETAIL_SP_FORWARD_HPP_INCLUDED

//  detail/sp_forward.hpp
//
//  Copyright 2008,2012 Peter Dimov
//
//  Distributed under the Boost Software License, Version 1.0.
//  See accompanying file LICENSE_1_0.txt or copy at
//  http://www.boost.org/LICENSE_1_0.txt

namespace ceto {

  namespace detail {

    template <class T>
    T &&sp_forward(T &t) noexcept {
      return static_cast<T &&>(t);
    }

  } // namespace detail

} // namespace ceto

#endif // #ifndef CETO_DETAIL_SP_FORWARD_HPP_INCLUDED
