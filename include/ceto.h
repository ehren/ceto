#ifndef CETO_H
#define CETO_H

#include <memory>
#include <vector>
#include <utility>
#include <type_traits>
#include <stdexcept>

#ifndef __clang__
#include <source_location>
#define CETO_HAS_SOURCE_LOCATION
#define CETO_SOURCE_LOC_PARAM , const std::source_location& location = std::source_location::current()
#define CETO_SOURCE_LOC_ARG location
#else
#define CETO_SOURCE_LOC_PARAM
#define CETO_SOURCE_LOC_ARG
#endif

namespace ceto {

struct object {
};

struct shared_object : public std::enable_shared_from_this<shared_object>, object {
    // shared_object should be managed by shared_ptr, a virtual destructor is not required (std::shared_ptr deleter does not polymorphically delete)
    // HOWEVER: https://github.com/pybind/pybind11/issues/1790 "Bug with inheritance, shared_ptr holder and enable_shared_from_this"
    virtual ~shared_object() = default;
};

// answer from https://stackoverflow.com/questions/657155/how-to-enable-shared-from-this-of-both-parent-and-derived/47789633#47789633
// (perhaps it's possible to use the accepted answer without freestanding funcs
//  however this solution works with template classes (naive insertion of:
//      const auto& self = std::static_pointer_cast<std::remove_reference<decltype((*this))>::type>(shared_from_this())
//  does not!)

template <typename Base>
inline std::shared_ptr<Base>
shared_from_base(std::enable_shared_from_this<Base>* base) {
    return base->shared_from_this();
}

template <typename Base>
inline std::shared_ptr<const Base>
shared_from_base(std::enable_shared_from_this<Base> const* base) {
    return base->shared_from_this();
}

template <typename That>
inline std::shared_ptr<That>
shared_from(That* that) {
    return std::static_pointer_cast<That>(shared_from_base(that));
}


class null_deref_error : public std::runtime_error
{
public:
    using std::runtime_error::runtime_error;
};

#ifdef CETO_HAS_SOURCE_LOCATION
    static inline std::string build_null_deref_message(const std::source_location& location) {
        std::string message = "Attempted null deref in attribute access:";
        message += location.file_name();
        message += ":";
        message += std::to_string(location.line());
        message += " (" + std::string(location.function_name()) + ")";
        message += " column " + std::to_string(location.column()) + "\n";
        return message;
    }
#else
    static inline std::string build_null_deref_message() {
        return "Attempted null deref in attribute access";
    }
#endif


// mad = maybe allow deref

// Based on answer of user Nawaz at https://stackoverflow.com/questions/14466620/c-template-specialization-calling-methods-on-types-that-could-be-pointers-or?noredirect=1&lq=1
// but with raw pointer autoderef removed and smart pointer (to ceto created classes) autoderef added.

// no autoderef
template<typename T>
T* mad(T & obj) {
    return std::addressof(obj);
}

// e.g. string temporaries
// no autoderef
template<typename T>
T* mad(T && obj) {
    return std::addressof(obj);
}

// autoderef
template<typename T>
std::enable_if_t<std::is_base_of_v<object, T>, std::shared_ptr<T>&>
mad(std::shared_ptr<T>& obj CETO_SOURCE_LOC_PARAM) {
    if (!obj) {
        throw null_deref_error(build_null_deref_message(CETO_SOURCE_LOC_ARG));
    }
    return obj;
}
// autoderef:
//template<typename T>
//std::enable_if_t<std::is_base_of_v<object, T>, std::shared_ptr<T>>
//mad(std::shared_ptr<T> obj) { return obj; }
// no need for a pass by value / return by value case it would seem


// autoderef of temporary
template<typename T>
std::enable_if_t<std::is_base_of_v<object, T>, std::shared_ptr<T>>  // could return std::shared_ptr<T>& here and remove the std::move
mad(std::shared_ptr<T>&& obj CETO_SOURCE_LOC_PARAM) {
    if (!obj) {
        throw null_deref_error(build_null_deref_message(CETO_SOURCE_LOC_ARG));
    }
    return std::move(obj);
}

// autoderef
template<typename T>
std::enable_if_t<std::is_base_of_v<object, T>, const std::shared_ptr<T>&>
mad(const std::shared_ptr<T>& obj CETO_SOURCE_LOC_PARAM) {
    if (!obj) {
        throw null_deref_error(build_null_deref_message(CETO_SOURCE_LOC_ARG));
    }
    return obj;
}

// autoderef
template<typename T>
std::enable_if_t<std::is_base_of_v<object, T>, std::unique_ptr<T>&>
mad(std::unique_ptr<T>& obj CETO_SOURCE_LOC_PARAM) {
    if (!obj) {
        throw null_deref_error(build_null_deref_message(CETO_SOURCE_LOC_ARG));
    }
    return obj;
}

// autoderef
template<typename T>
std::enable_if_t<std::is_base_of_v<object, T>, const std::unique_ptr<T>&>
mad(const std::unique_ptr<T>& obj CETO_SOURCE_LOC_PARAM) {
    if (!obj) {
        throw null_deref_error(build_null_deref_message(CETO_SOURCE_LOC_ARG));
    }
    return obj;
}

// autoderef of temporary
template<typename T>
std::enable_if_t<std::is_base_of_v<object, T>, std::unique_ptr<T>>  // could return std::unique_ptr<T>& here and remove the std::move
mad(std::unique_ptr<T>&& obj CETO_SOURCE_LOC_PARAM) {
    if (!obj) {
        throw null_deref_error(build_null_deref_message(CETO_SOURCE_LOC_ARG));
    }
    return std::move(obj);
}


// Automatic make_shared insertion. Works for many cases but currently unused (class lookup instead) due to relying on built-in C++ CTAD for [Foo(), Foo(), Foo()].
// (our manually implemented codegen (decltype of first element) from py14 still works with call_or_construct based construction).
// TODO consider re-enabling in certain contexts: would allow decltype(x)(1, 2) to result in a make_shared when x is a shared_ptr<shared_object> (this will fail in most cases now but may succeed undesirably in a few others e.g. decltype(x)() is an empty shared_ptr under naive class lookup when some might expect make_shared<decltype(*x)>()  (default constructor call)

template<typename T, typename... Args>
std::enable_if_t<std::is_base_of_v<shared_object, T>, std::shared_ptr<T>>
call_or_construct(Args&&... args) {
    // use braced args to disable narrowing conversions
    using TT = decltype(T{std::forward<Args>(args)...});
    return std::make_shared<TT>(std::forward<Args>(args)...);
}

template<typename T, typename... Args>
std::enable_if_t<std::is_base_of_v<shared_object, std::remove_const_t<T>> && std::is_const_v<T>, std::shared_ptr<T>>
call_or_construct(Args&&... args) {
    using tt = std::remove_const_t<T>;
    // use braced args to disable narrowing conversions
    using TT = const decltype(tt{std::forward<Args>(args)...});
    return std::make_shared<TT>(std::forward<Args>(args)...);
}

// no braced call for 0-args case - avoid needing to define an explicit no-arg constructor
template<typename T>
std::enable_if_t<std::is_base_of_v<shared_object, T>, std::shared_ptr<T>>
call_or_construct() {
    return std::make_shared<T>();
}

template<typename T, typename... Args>
std::enable_if_t<std::is_base_of_v<object, T> && !std::is_base_of_v<shared_object, T>, std::unique_ptr<T>>
call_or_construct(Args&&... args) {
    using TT = decltype(T{std::forward<Args>(args)...});
    return std::make_unique<TT>(std::forward<Args>(args)...);
}

template<typename T, typename... Args>
std::enable_if_t<std::is_base_of_v<object, std::remove_const_t<T>> && std::is_const_v<T> && !std::is_base_of_v<shared_object, std::remove_const_t<T>>, std::unique_ptr<T>>
call_or_construct(Args&&... args) {
    using tt = std::remove_const_t<T>;
    using TT = const decltype(tt{std::forward<Args>(args)...});
    return std::make_unique<TT>(std::forward<Args>(args)...);
}

template<typename T>
std::enable_if_t<std::is_base_of_v<object, T> && !std::is_base_of_v<shared_object, T>, std::unique_ptr<T>>
call_or_construct() {
    return std::make_unique<T>();
}

// non-object concrete classes/structs (in C++ sense)
template <typename T, typename... Args>
std::enable_if_t<!std::is_base_of_v<object, T> /*&& !std::is_void_v<T>*/, T>
call_or_construct(Args&&... args) {
    return T{std::forward<Args>(args)...};
}

template <typename T>
std::enable_if_t<!std::is_base_of_v<object, T> /*&& !std::is_void_v<T>*/, T>
call_or_construct() {
    return T();
}

// non-type template param version needed for e.g. construct_or_call<printf>("hi")
template<auto T, typename... Args>
auto
call_or_construct(Args&&... args) {
    return T(std::forward<Args>(args)...);
}

// template classes (forwarding to call_or_construct again seems to handle both object derived and plain classes)
template<template<class ...> class T, class... TArgs>
auto
call_or_construct(TArgs&&... args) {
    using TT = decltype(T(std::forward<TArgs>(args)...));
    return call_or_construct<TT>(T(std::forward<TArgs>(args)...));
}


// this one may be controversial (strong capture of shared object references by default - use 'weak' to break cycle)
template <class T>
std::enable_if_t<std::is_base_of_v<object, T>, std::shared_ptr<T>>
constexpr default_capture(std::shared_ptr<T> t) noexcept
{
    return t;
}

template <class T>
std::enable_if_t<std::is_arithmetic_v<T> || std::is_enum_v<T>, T>
constexpr default_capture(T t) noexcept
{
    return t;
}

// https://open-std.org/JTC1/SC22/WG21/docs/papers/2020/p0870r2.html#P0608R3
// still not in c++20 below is_convertible_without_narrowing implementation taken from
// https://github.com/GHF/mays/blob/db8b6b5556cc465d326d9e1acdc5483c70999b18/mays/internal/type_traits.h // (C) Copyright 2020 Xo Wang <xo@geekshavefeelings.com> // SPDX-License-Identifier: Apache-2.0

// True if |From| is implicitly convertible to |To| without going through a narrowing conversion.
// Will likely be included in C++2b through WG21 P0870 (see
// https://github.com/cplusplus/papers/issues/724).
template <typename From, typename To, typename Enable = void>
struct is_convertible_without_narrowing : std::false_type {};

// Implement "construct array of From" technique from P0870R4 with SFINAE instead of requires.
template <typename From, typename To>
struct is_convertible_without_narrowing<
    From,
    To,
    // NOLINTNEXTLINE(cppcoreguidelines-avoid-c-arrays,modernize-avoid-c-arrays)
    std::void_t<decltype(std::type_identity_t<To[]>{std::declval<From>()})>> : std::true_type {};

template <typename From, typename To>
constexpr bool is_convertible_without_narrowing_v =
    is_convertible_without_narrowing<From, To>::value;

static_assert(!is_convertible_without_narrowing_v<float, int>, "float -> int is narrowing!");


// for our own diy impl of "no narrowing conversions in local var definitions"
// that avoids some pitfalls always printing ceto "x: Type = y" as c++ "Type x {y}"
// e.g. ceto code "l : std.vector<int> = 1") should be an error not an aggregate
// initialization.
template <typename From, typename To>
inline constexpr bool is_non_aggregate_init_and_if_convertible_then_non_narrowing_v =
    std::is_aggregate_v<From> == std::is_aggregate_v<To> &&
    (!std::is_convertible_v<From, To> ||
     is_convertible_without_narrowing_v<From, To>);


// just let .at() do the bounds checking
auto maybe_bounds_check_access(auto&& v, auto&& index) -> decltype(auto)
    requires (std::is_integral_v<std::remove_cvref_t<decltype(index)>> &&
              requires { std::size(v); v.at(index); v[index]; } &&
              std::is_same_v<decltype(v.at(index)), decltype(v[index])>)
{
    return std::forward<decltype(v)>(v).at(std::forward<decltype(index)>(index));
}

auto maybe_bounds_check_access(auto&& v, auto&& index) -> decltype(auto)
    requires (!(std::is_integral_v<std::remove_cvref_t<decltype(index)>>))
{
    return std::forward<decltype(v)>(v)[std::forward<decltype(index)>(index)];
}

} // namespace ceto

#endif // CETO_H
