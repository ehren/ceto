#ifndef CETO_DETAIL_CHECKED_DELETE_HPP
#define CETO_DETAIL_CHECKED_DELETE_HPP

//
//  boost/checked_delete.hpp
//
//  Copyright (c) 2002, 2003 Peter Dimov
//  Copyright (c) 2003 Daniel Frey
//  Copyright (c) 2003 Howard Hinnant
//
//  Distributed under the Boost Software License, Version 1.0. (See
//  accompanying file LICENSE_1_0.txt or copy at
//  http://www.boost.org/LICENSE_1_0.txt)
//
//  See http://www.boost.org/libs/core/doc/html/core/checked_delete.html for documentation.
//

namespace ceto {

  // verify that types are complete for increased safety

  template <class T>
  inline void checked_delete(T *x) {
    // intentionally complex - simplification causes regressions
    typedef char type_must_be_complete[sizeof(T) ? 1 : -1];
    (void)sizeof(type_must_be_complete);
    delete x;
  }

  template <class T>
  inline void checked_array_delete(T *x) {
    typedef char type_must_be_complete[sizeof(T) ? 1 : -1];
    (void)sizeof(type_must_be_complete);
    delete[] x;
  }

  template <class T>
  struct checked_deleter {
    typedef void result_type;
    typedef T *argument_type;

    void operator()(T *x) const {
      // ceto:: disables ADL
      ceto::checked_delete(x);
    }
  };

  template <class T>
  struct checked_array_deleter {
    typedef void result_type;
    typedef T *argument_type;

    void operator()(T *x) const {
      ceto::checked_array_delete(x);
    }
  };

} // namespace ceto

#endif // #ifndef CETO_DETAIL_CHECKED_DELETE_HPP
