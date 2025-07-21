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

// TODO bunch of leading underscore usage from the libcxx implementation should be removed

#ifndef CETO_PROPAGATE_CONST
#define CETO_PROPAGATE_CONST

/*
    propagate_const synopsis

    namespace ceto {

    // [propagate_const]
    template <class T> class propagate_const;

    // [propagate_const.underlying], underlying pointer access
    constexpr const _Tp& get_underlying(const propagate_const<T>& pt) noexcept;
    constexpr T& get_underlying(propagate_const<T>& pt) noexcept;

    // [propagate_const.relational], relational operators
    template <class T> constexpr bool operator==(const propagate_const<T>& pt, std::nullptr_t);
    template <class T> constexpr bool operator==(std::nullptr_t, const propagate_const<T>& pu);
    template <class T> constexpr bool operator!=(const propagate_const<T>& pt, std::nullptr_t);
    template <class T> constexpr bool operator!=(std::nullptr_t, const propagate_const<T>& pu);
    template <class T, class U> constexpr bool operator==(const propagate_const<T>& pt, const propagate_const<_Up>& pu);
    template <class T, class U> constexpr bool operator!=(const propagate_const<T>& pt, const propagate_const<_Up>& pu);
    template <class T, class U> constexpr bool operator<(const propagate_const<T>& pt, const propagate_const<_Up>& pu);
    template <class T, class U> constexpr bool operator>(const propagate_const<T>& pt, const propagate_const<_Up>& pu);
    template <class T, class U> constexpr bool operator<=(const propagate_const<T>& pt, const propagate_const<_Up>& pu);
    template <class T, class U> constexpr bool operator>=(const propagate_const<T>& pt, const propagate_const<_Up>& pu);
    template <class T, class U> constexpr bool operator==(const propagate_const<T>& pt, const _Up& u);
    template <class T, class U> constexpr bool operator!=(const propagate_const<T>& pt, const _Up& u);
    template <class T, class U> constexpr bool operator<(const propagate_const<T>& pt, const _Up& u);
    template <class T, class U> constexpr bool operator>(const propagate_const<T>& pt, const _Up& u);
    template <class T, class U> constexpr bool operator<=(const propagate_const<T>& pt, const _Up& u);
    template <class T, class U> constexpr bool operator>=(const propagate_const<T>& pt, const _Up& u);
    template <class T, class U> constexpr bool operator==(const _Tp& t, const propagate_const<_Up>& pu);
    template <class T, class U> constexpr bool operator!=(const _Tp& t, const propagate_const<_Up>& pu);
    template <class T, class U> constexpr bool operator<(const _Tp& t, const propagate_const<_Up>& pu);
    template <class T, class U> constexpr bool operator>(const _Tp& t, const propagate_const<_Up>& pu);
    template <class T, class U> constexpr bool operator<=(const _Tp& t, const propagate_const<_Up>& pu);
    template <class T, class U> constexpr bool operator>=(const _Tp& t, const propagate_const<_Up>& pu);

    // [propagate_const.algorithms], specialized algorithms
    template <class T> constexpr void swap(propagate_const<T>& pt, propagate_const<T>& pu) noexcept(see below);

    template <class T>
    class propagate_const
    {

    public:
      typedef std::remove_reference_t<decltype(*declval<T&>())> element_type;

      // [propagate_const.ctor], constructors
      constexpr propagate_const() = default;
      propagate_const(const propagate_const& p) = default;  // ceto modification: changed to be copyable (defaulted instead of deleted)
      constexpr propagate_const(propagate_const&& p) = default;
      template <class U> EXPLICIT constexpr propagate_const(propagate_const<_Up>&& pu); // see below
      template <class U> EXPLICIT constexpr propagate_const(U&& u); // see below

      // [propagate_const.assignment], assignment
      propagate_const& operator=(const propagate_const& p) = default;  // ceto modification: changed to be copyable (defaulted instead of deleted)
      constexpr propagate_const& operator=(propagate_const&& p) = default;
      template <class U> constexpr propagate_const& operator=(propagate_const<_Up>&& pu);
      template <class U> constexpr propagate_const& operator=(U&& u); // see below

      // [propagate_const.const_observers], const observers
      explicit constexpr operator bool() const;
      constexpr const element_type* operator->() const;
      constexpr operator const element_type*() const; // Not always defined
      constexpr const element_type& operator*() const;
      constexpr const element_type* get() const;

      // [propagate_const.non_const_observers], non-const observers
      constexpr element_type* operator->();
      constexpr operator element_type*(); // Not always defined
      constexpr element_type& operator*();
      constexpr element_type* get();

      // [propagate_const.modifiers], modifiers
      constexpr void swap(propagate_const& pt) noexcept(see below)

    private:
      T t_; // exposition only
    };

  } // namespace ceto

  // [propagate_const.hash], hash support
  template <class T> struct hash<ceto::propagate_const<T>>;

  // [propagate_const.comparison_function_objects], comparison function objects
  template <class T> struct equal_to<ceto::propagate_const<T>>;
  template <class T> struct not_equal_to<ceto::propagate_const<T>>;
  template <class T> struct less<ceto::propagate_const<T>>;
  template <class T> struct greater<ceto::propagate_const<T>>;
  template <class T> struct less_equal<ceto::propagate_const<T>>;
  template <class T> struct greater_equal<ceto::propagate_const<T>>;

} // namespace std

*/

#include <functional>
#include <memory>
#include <type_traits>
#include <utility>


namespace ceto {

template <class _Tp>
class propagate_const;

template <class _Up>
inline constexpr const _Up& get_underlying(const propagate_const<_Up>& __pu) noexcept;

template <class _Up>
inline constexpr _Up& get_underlying(propagate_const<_Up>& __pu) noexcept;

template <class _Tp>
class propagate_const {
public:
  typedef std::remove_reference_t<decltype(*std::declval<_Tp&>())> element_type;

  static_assert(!std::is_array<_Tp>::value, "Instantiation of propagate_const with an array type is ill-formed.");
  static_assert(!std::is_reference<_Tp>::value, "Instantiation of propagate_const with a reference type is ill-formed.");
  static_assert(!(std::is_pointer<_Tp>::value && std::is_function<std::remove_pointer_t<_Tp> >::value),
                "Instantiation of propagate_const with a function-pointer type is ill-formed.");
  static_assert(!(std::is_pointer<_Tp>::value && std::is_same<std::remove_cv_t<std::remove_pointer_t<_Tp> >, void>::value),
                "Instantiation of propagate_const with a pointer to (possibly cv-qualified) void is ill-formed.");

private:
  template <class _Up>
  static constexpr element_type* __get_pointer(_Up* __u) {
    return __u;
  }

  template <class _Up>
  static constexpr element_type* __get_pointer(_Up& __u) {
    return __get_pointer(__u.get());
  }

  template <class _Up>
  static constexpr const element_type* __get_pointer(const _Up* __u) {
    return __u;
  }

  template <class _Up>
  static constexpr const element_type* __get_pointer(const _Up& __u) {
    return __get_pointer(__u.get());
  }

  template <class _Up>
  struct is_propagate_const : std::false_type {};

  template <class _Up>
  struct is_propagate_const<propagate_const<_Up>> : std::true_type {};

  _Tp __t_;

public:

  template <class _Up>
  friend constexpr const _Up& ceto::get_underlying(const propagate_const<_Up>& __pu) noexcept;
  template <class _Up>
  friend constexpr _Up& ceto::get_underlying(propagate_const<_Up>& __pu) noexcept;

  constexpr propagate_const() = default;

  propagate_const(const propagate_const&) = default;  // ceto modification: changed to be copyable (defaulted instead of deleted)

  constexpr propagate_const(propagate_const&&) = default;

  template <class _Up,
            std::enable_if_t<!std::is_convertible<_Up, _Tp>::value && std::is_constructible<_Tp, _Up&&>::value, bool> = true>
  explicit constexpr propagate_const(propagate_const<_Up>&& __pu)
      : __t_(std::move(ceto::get_underlying(__pu))) {}

  template <class _Up,
            std::enable_if_t<std::is_convertible<_Up&&, _Tp>::value && std::is_constructible<_Tp, _Up&&>::value, bool> = false>
  constexpr propagate_const(propagate_const<_Up>&& __pu)
      : __t_(std::move(ceto::get_underlying(__pu))) {}

  template <class _Up,
            std::enable_if_t<!std::is_convertible<_Up&&, _Tp>::value && std::is_constructible<_Tp, _Up&&>::value &&
                            !is_propagate_const<std::decay_t<_Up>>::value,
                        bool> = true>
  explicit constexpr propagate_const(_Up&& __u) : __t_(std::forward<_Up>(__u)) {}

  template <class _Up,
            std::enable_if_t<std::is_convertible<_Up&&, _Tp>::value && std::is_constructible<_Tp, _Up&&>::value &&
                            !is_propagate_const<std::decay_t<_Up>>::value,
                        bool> = false>
  constexpr propagate_const(_Up&& __u) : __t_(std::forward<_Up>(__u)) {}

  propagate_const& operator=(const propagate_const&) = default;  // ceto modification: changed to be copyable (defaulted instead of deleted)

  constexpr propagate_const& operator=(propagate_const&&) = default;

  // ceto modification: added this
  template <class _Up,
            std::enable_if_t< is_propagate_const<std::decay_t<_Up>>::value,
                        bool> = false>
  //constexpr propagate_const(_Up&& __u) : __t_(std::move(ceto::get_underlying(__u))) {}
  constexpr propagate_const(_Up&& __u) : __t_(ceto::get_underlying(__u)) {}


  /* ceto modification: disabled these 
  template <class _Up>
  constexpr propagate_const& operator=(propagate_const<_Up>&& __pu) {
    __t_ = std::move(ceto::get_underlying(__pu));
    return *this;
  }

  template <class _Up, class _Vp = std::enable_if_t<!is_propagate_const<std::decay_t<_Up>>::value>>
  constexpr propagate_const& operator=(_Up&& __u) {
    __t_ = std::forward<_Up>(__u);
    return *this;
  } */

  // ceto modification:: added this:
  template <class _Up, class _Vp = std::enable_if_t<is_propagate_const<std::decay_t<_Up>>::value>>
  constexpr propagate_const& operator=(_Up&& __u) {
    //__t_ = std::move(ceto::get_underlying(__u));
    __t_ = ceto::get_underlying(__u);
    return *this;
  }

  constexpr const element_type* get() const { return __get_pointer(__t_); }

  constexpr element_type* get() { return __get_pointer(__t_); }

  explicit constexpr operator bool() const { return get() != nullptr; }

  constexpr const element_type* operator->() const { return get(); }

  template <class _Dummy = _Tp, class _Up = std::enable_if_t<std::is_convertible< const _Dummy, const element_type*>::value>>
  constexpr operator const element_type*() const {
    return get();
  }

  constexpr const element_type& operator*() const { return *get(); }

  constexpr element_type* operator->() { return get(); }

  template <class _Dummy = _Tp, class _Up = std::enable_if_t< std::is_convertible<_Dummy, element_type*>::value>>
  constexpr operator element_type*() {
    return get();
  }

  constexpr element_type& operator*() { return *get(); }

  constexpr void swap(propagate_const& __pt) noexcept(std::is_nothrow_swappable_v<_Tp>) {
    using std::swap;
    swap(__t_, __pt.__t_);
  }
};

template <class _Tp>
constexpr bool operator==(const propagate_const<_Tp>& __pt, std::nullptr_t) {
  return ceto::get_underlying(__pt) == nullptr;
}

template <class _Tp>
constexpr bool operator==(std::nullptr_t, const propagate_const<_Tp>& __pt) {
  return nullptr == ceto::get_underlying(__pt);
}

template <class _Tp>
constexpr bool operator!=(const propagate_const<_Tp>& __pt, std::nullptr_t) {
  return ceto::get_underlying(__pt) != nullptr;
}

template <class _Tp>
constexpr bool operator!=(std::nullptr_t, const propagate_const<_Tp>& __pt) {
  return nullptr != ceto::get_underlying(__pt);
}

template <class _Tp, class _Up>
constexpr bool operator==(const propagate_const<_Tp>& __pt, const propagate_const<_Up>& __pu) {
  return ceto::get_underlying(__pt) == ceto::get_underlying(__pu);
}

template <class _Tp, class _Up>
constexpr bool operator!=(const propagate_const<_Tp>& __pt, const propagate_const<_Up>& __pu) {
  return ceto::get_underlying(__pt) != ceto::get_underlying(__pu);
}

template <class _Tp, class _Up>
constexpr bool operator<(const propagate_const<_Tp>& __pt, const propagate_const<_Up>& __pu) {
  return ceto::get_underlying(__pt) < ceto::get_underlying(__pu);
}

template <class _Tp, class _Up>
constexpr bool operator>(const propagate_const<_Tp>& __pt, const propagate_const<_Up>& __pu) {
  return ceto::get_underlying(__pt) > ceto::get_underlying(__pu);
}

template <class _Tp, class _Up>
constexpr bool operator<=(const propagate_const<_Tp>& __pt, const propagate_const<_Up>& __pu) {
  return ceto::get_underlying(__pt) <= ceto::get_underlying(__pu);
}

template <class _Tp, class _Up>
constexpr bool operator>=(const propagate_const<_Tp>& __pt, const propagate_const<_Up>& __pu) {
  return ceto::get_underlying(__pt) >= ceto::get_underlying(__pu);
}

template <class _Tp, class _Up>
constexpr bool operator==(const propagate_const<_Tp>& __pt, const _Up& __u) {
  return ceto::get_underlying(__pt) == __u;
}

template <class _Tp, class _Up>
constexpr bool operator!=(const propagate_const<_Tp>& __pt, const _Up& __u) {
  return ceto::get_underlying(__pt) != __u;
}

template <class _Tp, class _Up>
constexpr bool operator<(const propagate_const<_Tp>& __pt, const _Up& __u) {
  return ceto::get_underlying(__pt) < __u;
}

template <class _Tp, class _Up>
constexpr bool operator>(const propagate_const<_Tp>& __pt, const _Up& __u) {
  return ceto::get_underlying(__pt) > __u;
}

template <class _Tp, class _Up>
constexpr bool operator<=(const propagate_const<_Tp>& __pt, const _Up& __u) {
  return ceto::get_underlying(__pt) <= __u;
}

template <class _Tp, class _Up>
constexpr bool operator>=(const propagate_const<_Tp>& __pt, const _Up& __u) {
  return ceto::get_underlying(__pt) >= __u;
}

template <class _Tp, class _Up>
constexpr bool operator==(const _Tp& __t, const propagate_const<_Up>& __pu) {
  return __t == ceto::get_underlying(__pu);
}

template <class _Tp, class _Up>
constexpr bool operator!=(const _Tp& __t, const propagate_const<_Up>& __pu) {
  return __t != ceto::get_underlying(__pu);
}

template <class _Tp, class _Up>
constexpr bool operator<(const _Tp& __t, const propagate_const<_Up>& __pu) {
  return __t < ceto::get_underlying(__pu);
}

template <class _Tp, class _Up>
constexpr bool operator>(const _Tp& __t, const propagate_const<_Up>& __pu) {
  return __t > ceto::get_underlying(__pu);
}

template <class _Tp, class _Up>
constexpr bool operator<=(const _Tp& __t, const propagate_const<_Up>& __pu) {
  return __t <= ceto::get_underlying(__pu);
}

template <class _Tp, class _Up>
constexpr bool operator>=(const _Tp& __t, const propagate_const<_Up>& __pu) {
  return __t >= ceto::get_underlying(__pu);
}

template <class _Tp>
constexpr void
swap(propagate_const<_Tp>& __pc1, propagate_const<_Tp>& __pc2) noexcept(std::is_nothrow_swappable_v<_Tp>) {
  __pc1.swap(__pc2);
}

template <class _Tp>
constexpr const _Tp& get_underlying(const propagate_const<_Tp>& __pt) noexcept {
  return __pt.__t_;
}

template <class _Tp>
constexpr _Tp& get_underlying(propagate_const<_Tp>& __pt) noexcept {
  return __pt.__t_;
}

} // end namespace ceto

namespace std {

template <class _Tp>
struct hash<ceto::propagate_const<_Tp>> {
  typedef size_t result_type;
  typedef ceto::propagate_const<_Tp> argument_type;

  size_t operator()(const ceto::propagate_const<_Tp>& __pc1) const {
    return std::hash<_Tp>()(ceto::get_underlying(__pc1));
  }
};

template <class _Tp>
struct equal_to<ceto::propagate_const<_Tp>> {
  typedef ceto::propagate_const<_Tp> first_argument_type;
  typedef ceto::propagate_const<_Tp> second_argument_type;

  bool
  operator()(const ceto::propagate_const<_Tp>& __pc1, const ceto::propagate_const<_Tp>& __pc2) const {
    return std::equal_to<_Tp>()(ceto::get_underlying(__pc1), ceto::get_underlying(__pc2));
  }
};

template <class _Tp>
struct not_equal_to<ceto::propagate_const<_Tp>> {
  typedef ceto::propagate_const<_Tp> first_argument_type;
  typedef ceto::propagate_const<_Tp> second_argument_type;

  bool
  operator()(const ceto::propagate_const<_Tp>& __pc1, const ceto::propagate_const<_Tp>& __pc2) const {
    return std::not_equal_to<_Tp>()(ceto::get_underlying(__pc1), ceto::get_underlying(__pc2));
  }
};

template <class _Tp>
struct less<ceto::propagate_const<_Tp>> {
  typedef ceto::propagate_const<_Tp> first_argument_type;
  typedef ceto::propagate_const<_Tp> second_argument_type;

  bool
  operator()(const ceto::propagate_const<_Tp>& __pc1, const ceto::propagate_const<_Tp>& __pc2) const {
    return std::less<_Tp>()(ceto::get_underlying(__pc1), ceto::get_underlying(__pc2));
  }
};

template <class _Tp>
struct greater<ceto::propagate_const<_Tp>> {
  typedef ceto::propagate_const<_Tp> first_argument_type;
  typedef ceto::propagate_const<_Tp> second_argument_type;

  bool
  operator()(const ceto::propagate_const<_Tp>& __pc1, const ceto::propagate_const<_Tp>& __pc2) const {
    return std::greater<_Tp>()(ceto::get_underlying(__pc1), ceto::get_underlying(__pc2));
  }
};

template <class _Tp>
struct less_equal<ceto::propagate_const<_Tp>> {
  typedef ceto::propagate_const<_Tp> first_argument_type;
  typedef ceto::propagate_const<_Tp> second_argument_type;

  bool
  operator()(const ceto::propagate_const<_Tp>& __pc1, const ceto::propagate_const<_Tp>& __pc2) const {
    return std::less_equal<_Tp>()(ceto::get_underlying(__pc1), ceto::get_underlying(__pc2));
  }
};

template <class _Tp>
struct greater_equal<ceto::propagate_const<_Tp>> {
  typedef ceto::propagate_const<_Tp> first_argument_type;
  typedef ceto::propagate_const<_Tp> second_argument_type;

  bool
  operator()(const ceto::propagate_const<_Tp>& __pc1, const ceto::propagate_const<_Tp>& __pc2) const {
    return std::greater_equal<_Tp>()(ceto::get_underlying(__pc1), ceto::get_underlying(__pc2));
  }
};

} // end namespace std

#endif // CETO_PROPAGATE_CONST
