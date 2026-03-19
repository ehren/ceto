// -*- C++ -*-
//===----------------------------------------------------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

// Taken from https://github.com/llvm/llvm-project/blob/main/libcxx/include/experimental/propagate_const
// Commit b9a2658

// also informed by
// https://github.com/jbcoe/propagate_const
// https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2015/n4388.html
// JB Coe pull request: https://reviews.llvm.org/D12486#change-1YEhZEmd0Miu
//
// ceto Note: made copyable by defaulting the copy constructor and assignment operator
// See also https://github.com/jbcoe/deep_ptr and https://github.com/jbcoe/propagate_const/issues/33 (Non-copyable reduces applicability for helping library authors)
// In our case we need copyable because a non-copyable shared_ptr defeats the purpose of shared_ptr in the first place. 
// Also our aim is not "const implies thread safe" (it most certainly does not in general ceto code!) but at the least "the
// interprocedural transitive absence of 'mut' (and 'unsafe') implies C++ range-based-for safe".

// now has non null baked in (loosely inspired by gsl non_null but allows std::move to invalidate this guarantee - safe ceto code should rely on move from last use - std.move/std.forward requires unsafe.extern declaration)

#ifndef CETO_NON_NULL_PROPAGATE_CONST
#define CETO_NON_NULL_PROPAGATE_CONST

#define CETO_EXPERIMENTAL_NON_NULL

#include <functional>
#include <memory>
#include <type_traits>
#include <utility>
#include <optional>
#include <iostream>


namespace ceto {

template<typename T>
T&& ensure_not_null(T&& arg) {
#ifdef CETO_EXPERIMENTAL_NON_NULL
    if (std::forward<T>(arg) == nullptr) {
        std::cerr << "null check failed creating nonullpropconst (non null) from ordinary smart pointer\n";
        std::terminate();
    }
#endif
    return std::forward<T>(arg);
}

template <class Tp>
class nonullpropconst;

template <class Up>
struct is_nonullpropconst : std::false_type {};

template <class Up>
struct is_nonullpropconst<nonullpropconst<Up>> : std::true_type {};

template <typename T>
struct is_optional : std::false_type {};

template <typename T>
struct is_optional<std::optional<T>> : std::true_type {};

template <class Up>
inline constexpr const Up& get_underlying(const nonullpropconst<Up>& pu) noexcept;

template <class Up>
inline constexpr Up& get_underlying(nonullpropconst<Up>& pu) noexcept;

// tag type for bypassing null checks during construction (for our make_shared wrappers etc)
struct assume_non_null_t { explicit assume_non_null_t() = default; };
inline constexpr assume_non_null_t assume_non_null{};

template <class Tp>
class nonullpropconst {
public:
  typedef std::remove_reference_t<decltype(*std::declval<Tp&>())> element_type;

  static_assert(!std::is_array<Tp>::value, "Instantiation of nonullpropconst with an array type is ill-formed.");
  static_assert(!std::is_reference<Tp>::value, "Instantiation of nonullpropconst with a reference type is ill-formed.");
  static_assert(!(std::is_pointer<Tp>::value && std::is_function<std::remove_pointer_t<Tp> >::value),
                "Instantiation of nonullpropconst with a function-pointer type is ill-formed.");
  static_assert(!(std::is_pointer<Tp>::value && std::is_same<std::remove_cv_t<std::remove_pointer_t<Tp> >, void>::value),
                "Instantiation of nonullpropconst with a pointer to (possibly cv-qualified) void is ill-formed.");

private:
  template <class Up>
  static constexpr element_type* get_pointer(Up* u) {
    return u;
  }

  template <class Up>
  static constexpr element_type* get_pointer(Up& u) {
    return get_pointer(u.get());
  }

  template <class Up>
  static constexpr const element_type* get_pointer(const Up* u) {
    return u;
  }

  template <class Up>
  static constexpr const element_type* get_pointer(const Up& u) {
    return get_pointer(u.get());
  }

  Tp t_;

public:

  template <class Up>
  friend constexpr const Up& ceto::get_underlying(const nonullpropconst<Up>& pu) noexcept;
  template <class Up>
  friend constexpr Up& ceto::get_underlying(nonullpropconst<Up>& pu) noexcept;


// pybind11 requires a default constructible holder (maybe we can try nanobind instead; or maybe the new pybind11 3 py::smart_holder would allow our wrapper?) 
// workaround is to enable CETO_UNSAFE_ALLOW_PTR_DEFAULT_CONSTRUCTION for build of the compiler and defmacros (a little extra unsafety is ok at macro expansion time)
#if !defined(CETO_EXPERIMENTAL_NON_NULL) || defined(CETO_UNSAFE_ALLOW_NON_NULL_PTR_DEFAULT_CONSTRUCTION)
  constexpr nonullpropconst() = default;
#else
  nonullpropconst() = delete;
#endif


  nonullpropconst(const nonullpropconst&) = default;  // ceto modification: changed to be copyable (defaulted instead of deleted)

  constexpr nonullpropconst(nonullpropconst&&) = default;

  template <class Up,
            std::enable_if_t<!std::is_convertible<Up, Tp>::value && std::is_constructible<Tp, Up&&>::value, bool> = true>
  explicit constexpr nonullpropconst(nonullpropconst<Up>&& pu)
      : t_(std::move(ceto::get_underlying(pu))) {}

  template <class Up,
            std::enable_if_t<std::is_convertible<Up&&, Tp>::value && std::is_constructible<Tp, Up&&>::value, bool> = false>
  constexpr nonullpropconst(nonullpropconst<Up>&& pu)
      : t_(std::move(ceto::get_underlying(pu))) {}

  // ceto modification: added null checks to these

  template <class Up,
            std::enable_if_t<!std::is_convertible<Up&&, Tp>::value && std::is_constructible<Tp, Up&&>::value &&
                            !is_nonullpropconst<std::decay_t<Up>>::value,
                        bool> = true>
  explicit constexpr nonullpropconst(Up&& u) : t_(ensure_not_null(std::forward<Up>(u))) { }

  template <class Up,
            std::enable_if_t<std::is_convertible<Up&&, Tp>::value && std::is_constructible<Tp, Up&&>::value &&
                            !is_nonullpropconst<std::decay_t<Up>>::value,
                        bool> = false>
  constexpr nonullpropconst(Up&& u) : t_(ensure_not_null(std::forward<Up>(u))) { }

  // bypass null-check constructors (for our make_shared wrapper etc)
  template <class Up,
            std::enable_if_t<!std::is_convertible<Up&&, Tp>::value && std::is_constructible<Tp, Up&&>::value &&
                             !is_nonullpropconst<std::decay_t<Up>>::value,
                        bool> = true>
  explicit constexpr nonullpropconst(assume_non_null_t, Up&& u) : t_(std::forward<Up>(u)) { }

  template <class Up,
            std::enable_if_t<std::is_convertible<Up&&, Tp>::value && std::is_constructible<Tp, Up&&>::value &&
                             !is_nonullpropconst<std::decay_t<Up>>::value,
                        bool> = false>
  constexpr nonullpropconst(assume_non_null_t, Up&& u) : t_(std::forward<Up>(u)) { }

  nonullpropconst& operator=(const nonullpropconst&) = default;  // ceto modification: changed to be copyable (defaulted instead of deleted)

  constexpr nonullpropconst& operator=(nonullpropconst&&) = default;

  // ceto modification: added this
  template <class Up,
            std::enable_if_t< is_nonullpropconst<std::decay_t<Up>>::value,
                        bool> = false>
  //constexpr nonullpropconst(Up&& u) : t_(std::move(ceto::get_underlying(u))) {}
  constexpr nonullpropconst(Up&& u) : t_(ceto::get_underlying(u)) {}


  /* ceto modification: disabled these 
  template <class Up>
  constexpr nonullpropconst& operator=(nonullpropconst<Up>&& pu) {
    t_ = std::move(ceto::get_underlying(pu));
    return *this;
  }

  template <class Up, class Vp = std::enable_if_t<!is_nonullpropconst<std::decay_t<Up>>::value>>
  constexpr nonullpropconst& operator=(Up&& u) {
    t_ = std::forward<Up>(u);
    return *this;
  } */

  // ceto modification:: added this:
  template <class Up, class Vp = std::enable_if_t<is_nonullpropconst<std::decay_t<Up>>::value>>
  constexpr nonullpropconst& operator=(Up&& u) {
    //t_ = std::move(ceto::get_underlying(u));
    t_ = ceto::get_underlying(u);
    return *this;
  }

  // ceto modification:
  // prevent compilation when someone attempts to assign a null pointer constant
#ifdef CETO_EXPERIMENTAL_NON_NULL
  nonullpropconst(std::nullptr_t) = delete;
  nonullpropconst& operator=(std::nullptr_t) = delete;
#endif

  constexpr const element_type* get() const { return get_pointer(t_); }

  constexpr element_type* get() { return get_pointer(t_); }

#ifdef CETO_EXPERIMENTAL_NON_NULL
  explicit operator bool() const = delete;
#else
  explicit constexpr operator bool() const { return get() != nullptr; }
#endif

  constexpr const element_type* operator->() const { return get(); }

  template <class Dummy = Tp, class Up = std::enable_if_t<std::is_convertible< const Dummy, const element_type*>::value>>
  constexpr operator const element_type*() const {
    return get();
  }

  constexpr const element_type& operator*() const { return *get(); }

  constexpr element_type* operator->() { return get(); }

  // ceto modification: disabled this (seem like a bad idea to implicitly convert to a raw ptr)
  //template <class Dummy = Tp, class Up = std::enable_if_t< std::is_convertible<Dummy, element_type*>::value>>
  //constexpr operator element_type*() {
  //  return get();
  //}

  constexpr element_type& operator*() { return *get(); }

  constexpr void swap(nonullpropconst& pt) noexcept(std::is_nothrow_swappable_v<Tp>) {
    using std::swap;
    swap(t_, pt.t_);
  }
};

#ifdef CETO_EXPERIMENTAL_NON_NULL
template <class Tp>
constexpr bool operator==(const nonullpropconst<Tp>&, std::nullptr_t) = delete;

template <class Tp>
constexpr bool operator==(std::nullptr_t, const nonullpropconst<Tp>&) = delete;

template <class Tp>
constexpr bool operator!=(const nonullpropconst<Tp>&, std::nullptr_t) = delete;

template <class Tp>
constexpr bool operator!=(std::nullptr_t, const nonullpropconst<Tp>&) = delete;

#else
template <class Tp>
constexpr bool operator==(const nonullpropconst<Tp>& pt, std::nullptr_t) {
  return ceto::get_underlying(pt) == nullptr;
}

template <class Tp>
constexpr bool operator==(std::nullptr_t, const nonullpropconst<Tp>& pt) {
  return nullptr == ceto::get_underlying(pt);
}

template <class Tp>
constexpr bool operator!=(const nonullpropconst<Tp>& pt, std::nullptr_t) {
  return ceto::get_underlying(pt) != nullptr;
}

template <class Tp>
constexpr bool operator!=(std::nullptr_t, const nonullpropconst<Tp>& pt) {
  return nullptr != ceto::get_underlying(pt);
}
#endif

// ceto modification - these don't play well with optional wrapped nonullpropconst
/*
template <class Tp, class Up>
constexpr bool operator==(const nonullpropconst<Tp>& pt, const nonullpropconst<Up>& pu) {
  return ceto::get_underlying(pt) == ceto::get_underlying(pu);
}

template <class Tp, class Up>
constexpr bool operator!=(const nonullpropconst<Tp>& pt, const nonullpropconst<Up>& pu) {
  return ceto::get_underlying(pt) != ceto::get_underlying(pu);
}

template <class Tp, class Up>
constexpr bool operator<(const nonullpropconst<Tp>& pt, const nonullpropconst<Up>& pu) {
  return ceto::get_underlying(pt) < ceto::get_underlying(pu);
}

template <class Tp, class Up>
constexpr bool operator>(const nonullpropconst<Tp>& pt, const nonullpropconst<Up>& pu) {
  return ceto::get_underlying(pt) > ceto::get_underlying(pu);
}

template <class Tp, class Up>
constexpr bool operator<=(const nonullpropconst<Tp>& pt, const nonullpropconst<Up>& pu) {
  return ceto::get_underlying(pt) <= ceto::get_underlying(pu);
}

template <class Tp, class Up>
constexpr bool operator>=(const nonullpropconst<Tp>& pt, const nonullpropconst<Up>& pu) {
  return ceto::get_underlying(pt) >= ceto::get_underlying(pu);
}

template <class Tp, class Up>
constexpr bool operator==(const nonullpropconst<Tp>& pt, const Up& u) {
  return ceto::get_underlying(pt) == u;
}

template <class Tp, class Up>
constexpr bool operator!=(const nonullpropconst<Tp>& pt, const Up& u) {
  return ceto::get_underlying(pt) != u;
}

template <class Tp, class Up>
constexpr bool operator<(const nonullpropconst<Tp>& pt, const Up& u) {
  return ceto::get_underlying(pt) < u;
}

template <class Tp, class Up>
constexpr bool operator>(const nonullpropconst<Tp>& pt, const Up& u) {
  return ceto::get_underlying(pt) > u;
}

template <class Tp, class Up>
constexpr bool operator<=(const nonullpropconst<Tp>& pt, const Up& u) {
  return ceto::get_underlying(pt) <= u;
}

template <class Tp, class Up>
constexpr bool operator>=(const nonullpropconst<Tp>& pt, const Up& u) {
  return ceto::get_underlying(pt) >= u;
}

template <class Tp, class Up>
constexpr bool operator==(const Tp& t, const nonullpropconst<Up>& pu) {
  return t == ceto::get_underlying(pu);
}

template <class Tp, class Up>
constexpr bool operator!=(const Tp& t, const nonullpropconst<Up>& pu) {
  return t != ceto::get_underlying(pu);
}

template <class Tp, class Up>
constexpr bool operator<(const Tp& t, const nonullpropconst<Up>& pu) {
  return t < ceto::get_underlying(pu);
}

template <class Tp, class Up>
constexpr bool operator>(const Tp& t, const nonullpropconst<Up>& pu) {
  return t > ceto::get_underlying(pu);
}

template <class Tp, class Up>
constexpr bool operator<=(const Tp& t, const nonullpropconst<Up>& pu) {
  return t <= ceto::get_underlying(pu);
}

template <class Tp, class Up>
constexpr bool operator>=(const Tp& t, const nonullpropconst<Up>& pu) {
  return t >= ceto::get_underlying(pu);
}*/

// nonullpropconst vs nonullpropconst

template <class Tp, class Up>
constexpr bool operator==(const nonullpropconst<Tp>& pt, const nonullpropconst<Up>& pu) {
    return ceto::get_underlying(pt) == ceto::get_underlying(pu);
}

template <class Tp, class Up>
constexpr bool operator!=(const nonullpropconst<Tp>& pt, const nonullpropconst<Up>& pu) {
    return ceto::get_underlying(pt) != ceto::get_underlying(pu);
}

template <class Tp, class Up>
constexpr bool operator<(const nonullpropconst<Tp>& pt, const nonullpropconst<Up>& pu) {
    return ceto::get_underlying(pt) < ceto::get_underlying(pu);
}

template <class Tp, class Up>
constexpr bool operator>(const nonullpropconst<Tp>& pt, const nonullpropconst<Up>& pu) {
    return ceto::get_underlying(pt) > ceto::get_underlying(pu);
}

template <class Tp, class Up>
constexpr bool operator<=(const nonullpropconst<Tp>& pt, const nonullpropconst<Up>& pu) {
    return ceto::get_underlying(pt) <= ceto::get_underlying(pu);
}

template <class Tp, class Up>
constexpr bool operator>=(const nonullpropconst<Tp>& pt, const nonullpropconst<Up>& pu) {
    return ceto::get_underlying(pt) >= ceto::get_underlying(pu);
}

// nonullpropconst vs generic but not optional

#define CETO_PC_REL_OP(op) \
template <class Tp, class Up, \
          std::enable_if_t<!is_nonullpropconst<std::decay_t<Up>>::value && \
                           !is_optional<std::decay_t<Up>>::value, bool> = true> \
constexpr bool operator op(const nonullpropconst<Tp>& pt, const Up& u) { \
    return ceto::get_underlying(pt) op u; \
} \
template <class Tp, class Up, \
          std::enable_if_t<!is_nonullpropconst<std::decay_t<Tp>>::value && \
                           !is_optional<std::decay_t<Tp>>::value, bool> = true> \
constexpr bool operator op(const Tp& t, const nonullpropconst<Up>& pu) { \
    return t op ceto::get_underlying(pu); \
}

CETO_PC_REL_OP(==)
CETO_PC_REL_OP(!=)

// these aren't a great idea unless you're wrapping raw pointers
//CETO_PC_REL_OP(<)
//CETO_PC_REL_OP(>)
//CETO_PC_REL_OP(<=)
//CETO_PC_REL_OP(>=)

#undef CETO_PC_REL_OP

template <class Tp>
constexpr void
swap(nonullpropconst<Tp>& pc1, nonullpropconst<Tp>& pc2) noexcept(std::is_nothrow_swappable_v<Tp>) {
  pc1.swap(pc2);
}

template <class Tp>
constexpr const Tp& get_underlying(const nonullpropconst<Tp>& pt) noexcept {
  return pt.t_;
}

template <class Tp>
constexpr Tp& get_underlying(nonullpropconst<Tp>& pt) noexcept {
  return pt.t_;
}

} // end namespace ceto

namespace std {

template <class Tp>
struct hash<ceto::nonullpropconst<Tp>> {
  typedef size_t result_type;
  typedef ceto::nonullpropconst<Tp> argument_type;

  size_t operator()(const ceto::nonullpropconst<Tp>& pc1) const {
    return std::hash<Tp>()(ceto::get_underlying(pc1));
  }
};

template <class Tp>
struct equal_to<ceto::nonullpropconst<Tp>> {
  typedef ceto::nonullpropconst<Tp> first_argument_type;
  typedef ceto::nonullpropconst<Tp> second_argument_type;

  bool
  operator()(const ceto::nonullpropconst<Tp>& pc1, const ceto::nonullpropconst<Tp>& pc2) const {
    return std::equal_to<Tp>()(ceto::get_underlying(pc1), ceto::get_underlying(pc2));
  }
};

template <class Tp>
struct not_equal_to<ceto::nonullpropconst<Tp>> {
  typedef ceto::nonullpropconst<Tp> first_argument_type;
  typedef ceto::nonullpropconst<Tp> second_argument_type;

  bool
  operator()(const ceto::nonullpropconst<Tp>& pc1, const ceto::nonullpropconst<Tp>& pc2) const {
    return std::not_equal_to<Tp>()(ceto::get_underlying(pc1), ceto::get_underlying(pc2));
  }
};

template <class Tp>
struct less<ceto::nonullpropconst<Tp>> {
  typedef ceto::nonullpropconst<Tp> first_argument_type;
  typedef ceto::nonullpropconst<Tp> second_argument_type;

  bool
  operator()(const ceto::nonullpropconst<Tp>& pc1, const ceto::nonullpropconst<Tp>& pc2) const {
    return std::less<Tp>()(ceto::get_underlying(pc1), ceto::get_underlying(pc2));
  }
};

template <class Tp>
struct greater<ceto::nonullpropconst<Tp>> {
  typedef ceto::nonullpropconst<Tp> first_argument_type;
  typedef ceto::nonullpropconst<Tp> second_argument_type;

  bool
  operator()(const ceto::nonullpropconst<Tp>& pc1, const ceto::nonullpropconst<Tp>& pc2) const {
    return std::greater<Tp>()(ceto::get_underlying(pc1), ceto::get_underlying(pc2));
  }
};

template <class Tp>
struct less_equal<ceto::nonullpropconst<Tp>> {
  typedef ceto::nonullpropconst<Tp> first_argument_type;
  typedef ceto::nonullpropconst<Tp> second_argument_type;

  bool
  operator()(const ceto::nonullpropconst<Tp>& pc1, const ceto::nonullpropconst<Tp>& pc2) const {
    return std::less_equal<Tp>()(ceto::get_underlying(pc1), ceto::get_underlying(pc2));
  }
};

template <class Tp>
struct greater_equal<ceto::nonullpropconst<Tp>> {
  typedef ceto::nonullpropconst<Tp> first_argument_type;
  typedef ceto::nonullpropconst<Tp> second_argument_type;

  bool
  operator()(const ceto::nonullpropconst<Tp>& pc1, const ceto::nonullpropconst<Tp>& pc2) const {
    return std::greater_equal<Tp>()(ceto::get_underlying(pc1), ceto::get_underlying(pc2));
  }
};

} // end namespace std

#endif // CETO_NON_NULL_PROPAGATE_CONST
