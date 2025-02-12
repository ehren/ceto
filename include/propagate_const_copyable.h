/*

Copyright (c) 2014-2018 Jonathan B. Coe

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

*/

// Taken from https://github.com/jbcoe/propagate_const but modified to be copyable
// last commit https://github.com/jbcoe/propagate_const/commit/dd8723deb19e3ac2e34ec1fb91c9bd641872f0f6

#ifndef CETO_PROPAGATE_CONST_INCLUDED
#define CETO_PROPAGATE_CONST_INCLUDED

#include <functional>
#include <memory>
#include <type_traits>
#include <utility>

#ifdef _MSC_VER
#if _MSC_VER <= 1900 // MSVS 2015 and earlier
#error "Not supported"
#endif
#endif

namespace ceto {

template <class T>
class propagate_const {
 public:
 using element_type = typename std::pointer_traits<T>::element_type;

 private:
  template <class U>
  static element_type* get_pointer(U* u) {
    return u;
  }

  template <class U>
  static element_type* get_pointer(U& u) {
    return get_pointer(u.get());
  }

  template <class U>
  static const element_type* get_pointer(const U* u) {
    return u;
  }

  template <class U>
  static const element_type* get_pointer(const U& u) {
    return get_pointer(u.get());
  }

  template <class U>
  struct is_propagate_const : std::false_type {};

  template <class U>
  struct is_propagate_const<propagate_const<U>> : std::true_type {};

 public:
  // [propagate_const.ctor], constructors
  constexpr propagate_const() = default;

  propagate_const(const propagate_const& p) = default;   // ceto modification: changed from 'delete' to 'default'

  constexpr propagate_const(propagate_const&& p) = default;

  //
  // Use SFINAE to check if converting constructor should be explicit.
  //
  template <class U, std::enable_if_t<!std::is_convertible<U&&, T>::value &&
                                     std::is_constructible<T, U&&>::value,
                                 bool> = true>
  explicit constexpr propagate_const(propagate_const<U>&& pu)
      : t_(std::move(pu.t_)) {}

  template <class U, std::enable_if_t<std::is_convertible<U&&, T>::value &&
                                     std::is_constructible<T, U&&>::value,
                                 bool> = false>
  constexpr propagate_const(propagate_const<U>&& pu) : t_(std::move(pu.t_)) {}

  template <class U, std::enable_if_t<!std::is_convertible<U&&, T>::value &&
                                     std::is_constructible<T, U&&>::value &&
                                     !is_propagate_const<std::decay_t<U>>::value,
                                 bool> = true>
  explicit constexpr propagate_const(U&& u) : t_(std::forward<U>(u)) {}

  template <class U, std::enable_if_t<std::is_convertible<U&&, T>::value &&
                                     std::is_constructible<T, U&&>::value &&
                                     !is_propagate_const<std::decay_t<U>>::value,
                                 bool> = false>
  constexpr propagate_const(U&& u) : t_(std::forward<U>(u)) {}

  // [propagate_const.assignment], assignment
  propagate_const& operator=(const propagate_const& p) = default;  // ceto modification: changed from 'delete' to 'default'

  constexpr propagate_const& operator=(propagate_const&& p) = default;

  template <class U>
  constexpr propagate_const& operator=(propagate_const<U>&& pu) {
    t_ = std::move(pu.t_);
    return *this;
  }

  template <class U,
            class = std::enable_if_t<!is_propagate_const<std::decay_t<U>>::value>>
  constexpr propagate_const& operator=(U&& u) {
    t_ = std::move(u);
    return *this;
  }

  // [propagate_const.const_observers], const observers
  explicit constexpr operator bool() const { return get() != nullptr; }
  constexpr const element_type* operator->() const { return get(); }

  template <class T_ = T, class U = std::enable_if_t<std::is_convertible<
                              const T_, const element_type*>::value>>
  constexpr operator const element_type*() const  // Not always defined
  {
    return get();
  }

  constexpr const element_type& operator*() const { return *get(); }

  constexpr const element_type* get() const { return get_pointer(t_); }

  // [propagate_const.non_const_observers], non-const observers
  constexpr element_type* operator->() { return get(); }

  template <class T_ = T,
            class U = std::enable_if_t<std::is_convertible<T_, element_type*>::value>>
  constexpr operator element_type*()  // Not always defined
  {
    return get();
  }

  constexpr element_type& operator*() { return *get(); }

  constexpr element_type* get() { return get_pointer(t_); }
  
  // [propagate_const.modifiers], modifiers
  constexpr void swap(propagate_const& pt) noexcept(
      noexcept(swap(std::declval<T&>(), std::declval<T&>()))) {
    swap(t_, pt.t_);
  }

 private:
  T t_;

  friend struct std::hash<propagate_const<T>>;
  friend struct std::equal_to<propagate_const<T>>;
  friend struct std::not_equal_to<propagate_const<T>>;
  friend struct std::greater<propagate_const<T>>;
  friend struct std::less<propagate_const<T>>;
  friend struct std::greater_equal<propagate_const<T>>;
  friend struct std::less_equal<propagate_const<T>>;

  // [propagate_const.relational], relational operators
  friend constexpr bool operator==(const propagate_const& pt, nullptr_t) {
    return pt.t_ == nullptr;
  }

  friend constexpr bool operator==(nullptr_t, const propagate_const& pu) {
    return nullptr == pu.t_;
  }

  friend constexpr bool operator!=(const propagate_const& pt, nullptr_t) {
    return pt.t_ != nullptr;
  }

  friend constexpr bool operator!=(nullptr_t, const propagate_const& pu) {
    return nullptr != pu.t_;
  }

  template <class U>
  friend constexpr bool operator==(const propagate_const& pt,
                                   const propagate_const<U>& pu) {
    return pt.t_ == pu.t_;
  }

  template <class U>
  friend constexpr bool operator!=(const propagate_const& pt,
                                   const propagate_const<U>& pu) {
    return pt.t_ != pu.t_;
  }

  template <class U>
  friend constexpr bool operator<(const propagate_const& pt,
                                  const propagate_const<U>& pu) {
    return pt.t_ < pu.t_;
  }

  template <class U>
  friend constexpr bool operator>(const propagate_const& pt,
                                  const propagate_const<U>& pu) {
    return pt.t_ > pu.t_;
  }

  template <class U>
  friend constexpr bool operator<=(const propagate_const& pt,
                                   const propagate_const<U>& pu) {
    return pt.t_ <= pu.t_;
  }

  template <class U>
  friend constexpr bool operator>=(const propagate_const& pt,
                                   const propagate_const<U>& pu) {
    return pt.t_ >= pu.t_;
  }

  template <class U,
            class = std::enable_if_t<!is_propagate_const<std::decay_t<U>>::value>>
  friend constexpr bool operator==(const propagate_const& pt, const U& u) {
    return pt.t_ == u;
  }

  template <class U,
            class = std::enable_if_t<!is_propagate_const<std::decay_t<U>>::value>>
  friend constexpr bool operator!=(const propagate_const& pt, const U& u) {
    return pt.t_ != u;
  }

  template <class U,
            class = std::enable_if_t<!is_propagate_const<std::decay_t<U>>::value>>
  friend constexpr bool operator<(const propagate_const& pt, const U& u) {
    return pt.t_ < u;
  }

  template <class U,
            class = std::enable_if_t<!is_propagate_const<std::decay_t<U>>::value>>
  friend constexpr bool operator>(const propagate_const& pt, const U& u) {
    return pt.t_ > u;
  }

  template <class U,
            class = std::enable_if_t<!is_propagate_const<std::decay_t<U>>::value>>
  friend constexpr bool operator<=(const propagate_const& pt, const U& u) {
    return pt.t_ <= u;
  }

  template <class U,
            class = std::enable_if_t<!is_propagate_const<std::decay_t<U>>::value>>
  friend constexpr bool operator>=(const propagate_const& pt, const U& u) {
    return pt.t_ >= u;
  }

  template <class U,
            class = std::enable_if_t<!is_propagate_const<std::decay_t<U>>::value>>
  friend constexpr bool operator==(const U& u, const propagate_const& pu) {
    return u == pu.t_;
  }

  template <class U,
            class = std::enable_if_t<!is_propagate_const<std::decay_t<U>>::value>>
  friend constexpr bool operator!=(const U& u, const propagate_const& pu) {
    return u != pu.t_;
  }

  template <class U,
            class = std::enable_if_t<!is_propagate_const<std::decay_t<U>>::value>>
  friend constexpr bool operator<(const U& u, const propagate_const& pu) {
    return u < pu.t_;
  }

  template <class U,
            class = std::enable_if_t<!is_propagate_const<std::decay_t<U>>::value>>
  friend constexpr bool operator>(const U& u, const propagate_const& pu) {
    return u > pu.t_;
  }

  template <class U,
            class = std::enable_if_t<!is_propagate_const<std::decay_t<U>>::value>>
  friend constexpr bool operator<=(const U& u, const propagate_const& pu) {
    return u <= pu.t_;
  }

  template <class U,
            class = std::enable_if_t<!is_propagate_const<std::decay_t<U>>::value>>
  friend constexpr bool operator>=(const U& u, const propagate_const& pu) {
    return u >= pu.t_;
  }
};


// [propagate_const.algorithms], specialized algorithms
template <class T>
constexpr void swap(propagate_const<T>& pt, propagate_const<T>& pu) noexcept(
    noexcept(swap(std::declval<T&>(), std::declval<T&>())))
{
  swap(pt.underlying_ptr(), pu.underlying_ptr());
}


// ceto note - something wacky - underlying_ptr not implemented?

// this taken from 
// https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2015/n4388.html
// and
// https://reviews.llvm.org/D12486

template <class Tp>
constexpr const Tp& get_underlying(const propagate_const<Tp>& pt) noexcept
{
  return pt._t;
}

template <class Tp>
Tp& get_underlying(propagate_const<Tp>& pt) noexcept
{
  return pt._t;
}

}  //  end namespace ceto

namespace std {

// [propagate_const.hash], hash support
template <class T>
struct hash<ceto::propagate_const<T>> {
  typedef size_t result_type;
  typedef ceto::propagate_const<T> argument_type;

  bool operator()(
      const ceto::propagate_const<T>& pc) const {
    return std::hash<T>()(pc.t_);
  }
};

// [propagate_const.comparison_function_objects], comparison function objects
template <class T>
struct equal_to<ceto::propagate_const<T>> {
  typedef ceto::propagate_const<T> first_argument_type;
  typedef ceto::propagate_const<T>
      second_argument_type;

  bool operator()(
      const ceto::propagate_const<T>& pc1,
      const ceto::propagate_const<T>& pc2) const {
    return std::equal_to<T>()(pc1.t_, pc2.t_);
  }
};

template <class T>
struct not_equal_to<ceto::propagate_const<T>> {
  typedef ceto::propagate_const<T> first_argument_type;
  typedef ceto::propagate_const<T>
      second_argument_type;

  bool operator()(
      const ceto::propagate_const<T>& pc1,
      const ceto::propagate_const<T>& pc2) const {
    return std::not_equal_to<T>()(pc1.t_, pc2.t_);
  }
};

template <class T>
struct less<ceto::propagate_const<T>> {
  typedef ceto::propagate_const<T> first_argument_type;
  typedef ceto::propagate_const<T>
      second_argument_type;

  bool operator()(
      const ceto::propagate_const<T>& pc1,
      const ceto::propagate_const<T>& pc2) const {
    return std::less<T>()(pc1.t_, pc2.t_);
  }
};

template <class T>
struct greater<ceto::propagate_const<T>> {
  typedef ceto::propagate_const<T> first_argument_type;
  typedef ceto::propagate_const<T>
      second_argument_type;

  bool operator()(
      const ceto::propagate_const<T>& pc1,
      const ceto::propagate_const<T>& pc2) const {
    return std::greater<T>()(pc1.t_, pc2.t_);
  }
};

template <class T>
struct less_equal<ceto::propagate_const<T>> {
  typedef ceto::propagate_const<T> first_argument_type;
  typedef ceto::propagate_const<T>
      second_argument_type;

  bool operator()(
      const ceto::propagate_const<T>& pc1,
      const ceto::propagate_const<T>& pc2) const {
    return std::less_equal<T>()(pc1.t_, pc2.t_);
  }
};

template <class T>
struct greater_equal<ceto::propagate_const<T>> {
  typedef ceto::propagate_const<T> first_argument_type;
  typedef ceto::propagate_const<T>
      second_argument_type;

  bool operator()(
      const ceto::propagate_const<T>& pc1,
      const ceto::propagate_const<T>& pc2) const {
    return std::greater_equal<T>()(pc1.t_, pc2.t_);
  }
};

}  // end namespace std

#endif // CETO_PROPAGATE_CONST_INCLUDED
