#ifndef CETO_H
#define CETO_H

#include <memory>
#include <vector>
#include <utility>
#include <type_traits>
#include <optional>
#include <iostream>
#include <ranges>

#if defined(__cpp_lib_source_location)
#include <source_location>
// note "def (foo, x, y, loc = std.source_location.current():" is a macro (see boundscheck.cth)
#define CETO_HAS_SOURCE_LOCATION
#define CETO_PRIVATE_SOURCE_LOC_PARAM , const std::source_location& location = std::source_location::current()
#define CETO_PRIVATE_SOURCE_LOC_ARG location
#else
#define CETO_PRIVATE_SOURCE_LOC_PARAM
#define CETO_PRIVATE_SOURCE_LOC_ARG
#endif

#if !_MSC_VER
// although we currently use ceto::propagate_const for shared and unique
// classes we could potentially use std::experimental::propagate_const
// for :unique in the future (unsuported with MSVC)
#include <experimental/propagate_const>
#define CETO_HAS_PROP_CONST_STD_EXP
#endif

#ifdef CETO_USING_GODBOLT
// godbolt only supports single header library includes via url
// also remember to manually: #include "https://raw.githubusercontent.com/ehren/ceto/refs/heads/main/include/propagate_const_copyable.h"
namespace ceto {
    template <typename T>
    using local_shared_ptr = std::shared_ptr<T>;
}
#else
#include "propagate_const_copyable.h"
#include "kit_local_shared_ptr/smart_ptr.hpp"
#endif

namespace ceto {

template <typename T>
concept IsBasicStrongPtr = std::same_as<T, std::shared_ptr<typename T::element_type>> ||
                           std::same_as<T, std::unique_ptr<typename T::element_type>> ||
                           std::same_as<T, ceto::local_shared_ptr<typename T::element_type>>;

template <typename T>
concept IsBasicWeakPtr = std::same_as<T, std::weak_ptr<typename T::element_type>>;

template <class T>
struct is_propagate_const_copyable : std::false_type {};

#if defined(CETO_HAS_PROP_CONST_STD_EXP)
template <class T>
struct is_propagate_const_noncopyable : std::false_type {};

template <class T>
struct is_propagate_const_noncopyable<std::experimental::propagate_const<T>> : std::true_type {};
#endif

template <class T>
struct is_propagate_const_copyable<ceto::propagate_const<T>> : std::true_type {};

template <typename T>
concept IsStrongPtr = IsBasicStrongPtr<std::remove_cvref_t<T>>
                      || (is_propagate_const_copyable<std::remove_cvref_t<T>>::value && IsBasicStrongPtr<std::remove_cvref_t<decltype(ceto::get_underlying(std::declval<T>()))>>)
#if defined(CETO_HAS_PROP_CONST_STD_EXP)
                      || (is_propagate_const_noncopyable<std::remove_cvref_t<T>>::value && IsBasicStrongPtr<std::remove_cvref_t<decltype(std::experimental::get_underlying(std::declval<T>()))>>)
#endif
                      ;

template <typename T>
concept IsWeakPtr = IsBasicWeakPtr<std::remove_cvref_t<T>> ||
                    (is_propagate_const_copyable<std::remove_cvref_t<T>>::value && IsBasicWeakPtr<std::remove_cvref_t<decltype(ceto::get_underlying(std::declval<T>()))>>);

template <typename T>
concept IsOptional = std::same_as<std::remove_cvref_t<T>, std::optional<typename std::remove_cvref_t<T>::value_type>>;

template<typename T>
concept IsDereferencable = requires (T t) {
    *t;
};

template<typename T>
concept IsRawDereferencable = IsDereferencable<T> && !IsOptional<T> && !IsStrongPtr<T> && !IsWeakPtr<T>;

struct object {
};

struct shared_object : object {
};

struct enable_shared_from_this_base_for_templates : public std::enable_shared_from_this<enable_shared_from_this_base_for_templates>, public shared_object  {
    // want this for template classes (perhaps a bit dubious). For classes whose
    // type depends on a single constructor call (via ctad) we could do better
    // e.g std::enable_shared_from_this<decltype(Foo{std::declval<int>(), ...})>
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
inline ceto::propagate_const<std::shared_ptr<That>>
shared_from(That* that) {
    return ceto::propagate_const<std::shared_ptr<That>>(std::static_pointer_cast<That>(shared_from_base(that)));
}

#ifdef CETO_HAS_SOURCE_LOCATION
static inline void issue_null_deref_message(const std::source_location& location) {
    std::cerr << "Attempted null autoderef in attribute access:";
    std::cerr << location.file_name();
    std::cerr << ":";
    std::cerr << std::to_string(location.line());
    std::cerr << " (" + std::string(location.function_name()) + ")";
    std::cerr << " column " + std::to_string(location.column()) << std::endl;
}

#else
static inline void issue_null_deref_message() {
    std::cerr << "Attempted null autoderef." << std::endl;
}

#endif

struct EndLoopMarker : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

#define CETO_BAN_REFS(expr) [&]() -> decltype(auto) { static_assert(!(std::is_reference_v<decltype((expr))>)); return expr; }()

// mad = maybe allow deref

// Based on answer of Nawaz at https://stackoverflow.com/questions/14466620/c-template-specialization-calling-methods-on-types-that-could-be-pointers-or?noredirect=1&lq=1
// but using concepts and with raw pointer autoderef removed and smart pointer autoderef added.

// autoderef
template<typename T>
auto mad_smartptr(T&& obj CETO_PRIVATE_SOURCE_LOC_PARAM) -> decltype(auto) requires IsStrongPtr<T> {
    if (!std::forward<T>(obj)) {
        issue_null_deref_message(CETO_PRIVATE_SOURCE_LOC_ARG);
        std::terminate();
    }
    return std::forward<T>(obj);
}

// no autoderef
template<typename T>
auto mad_smartptr(T&& obj CETO_PRIVATE_SOURCE_LOC_PARAM) -> decltype(auto) requires (!IsStrongPtr<T>) {
    // no std::forward here:
    // https://en.cppreference.com/w/cpp/memory/addressof says:
    // Rvalue overload is deleted to prevent taking the address of const rvalues.
    return std::addressof(obj);
}

// autoderef optional or smart ptr:
// In contrast to the mad_smartptr case, these are not used when calling a possible method of std::optional
// e.g. my_optional.value() calls std::optional::value() whereas my_object.get() calls the underlying get()
// method of my_object (or produces an error) rather than calling e.g. std::shared_ptr::get())

template<typename T>
auto mad(T&& obj CETO_PRIVATE_SOURCE_LOC_PARAM) -> decltype(auto) requires IsOptional<T> {
    if (!std::forward<T>(obj)) {
        issue_null_deref_message(CETO_PRIVATE_SOURCE_LOC_ARG);
        std::terminate();
    }

    // maybe a double autoderef (though optional of nullable smart ptr should be discouraged)
#ifdef CETO_HAS_SOURCE_LOCATION
    return mad_smartptr(std::forward<T>(obj).value(), CETO_PRIVATE_SOURCE_LOC_ARG);
#else
    return mad_smartptr(std::forward<T>(obj).value());
#endif
}

// no autoderef of optional - maybe still autoderef smart pointer
template<typename T>
auto mad(T&& obj CETO_PRIVATE_SOURCE_LOC_PARAM) -> decltype(auto) requires (!IsOptional<T>) {
#ifdef CETO_HAS_SOURCE_LOCATION
    return mad_smartptr(std::forward<T>(obj), CETO_PRIVATE_SOURCE_LOC_ARG);
#else
    return mad_smartptr(std::forward<T>(obj));
#endif
}

// construction wrappers

template<typename T, typename... A>
auto make_shared_propagate_const(A&&... args) -> auto {
    return ceto::propagate_const<std::shared_ptr<T>>(std::make_shared<T>(std::forward<A>(args)...));
}

template<typename T, typename... A>
auto make_unique_propagate_const(A&&... args) -> auto {
    return ceto::propagate_const<std::unique_ptr<T>>(std::make_unique<T>(std::forward<A>(args)...));
}

// Notes regarding a non-removed call_or_construct implementation (resurrecting it would require fixing breakage since introducing const by default / propagate_const by default:
// ceto::call_or_construct() works for many cases but currently unused (class lookup instead) due to relying on built-in C++ CTAD for [Foo(), Foo(), Foo()].
// (our manually implemented codegen (decltype of first element) from py14 still works with call_or_construct based construction).
// TODO consider re-enabling in certain contexts: would allow decltype(x)(1, 2) to result in a make_shared when x is a shared_ptr<shared_object> (this will fail in most cases now but may succeed undesirably in a few others e.g. decltype(x)() is an empty shared_ptr under naive class lookup when some might expect make_shared<decltype(*x)>()  (default constructor call)

// this one may be controversial (strong capture of shared object references by default - use 'weak' to break cycle)
template <class T>
std::enable_if_t<std::is_base_of_v<object, T>, const ceto::propagate_const<std::shared_ptr<T>>>  // We now autoderef all shared/unique_ptrs not just to ceto class instances. doing the same for lambda capture might go a bit too far - don't want to encourange writing shared_ptr<vector<int>> instead of creating a wrapper class instance that's automatically placed in the capture list
constexpr default_capture(ceto::propagate_const<std::shared_ptr<T>> t) {
    return t;
}

template <class T>
std::enable_if_t<std::is_base_of_v<object, T>, const std::weak_ptr<T>>
constexpr default_capture(std::weak_ptr<T> t) {
    return t;
}

template <class T>
std::enable_if_t<std::is_arithmetic_v<T> || std::is_enum_v<T>, const T>
constexpr default_capture(T t) {
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

template <typename T>
concept IsContainer = requires(T t)
{
    std::begin(t);
    std::end(t);
};

// only applied to known callables
template <typename T>
concept IsStateless = std::is_empty_v<std::remove_cvref_t<T>> &&
                      std::is_class_v<std::remove_cvref_t<T>>;

template<typename Container>
concept ContiguousContainer = requires(Container c) {
    std::begin(c) + 2;
    std::end(c);
    std::size(c);
    c[0];
};

template <typename T>
concept OwningContainer = IsContainer<std::remove_cvref_t<T>> && requires(std::remove_cvref_t<T> t) {
    t.clear();
    typename T::allocator_type;
};


// with c++23 could also allow std::ranges::repeat_view
template<typename T>
inline constexpr bool is_iota_view_v = false;

template<typename W, typename B>
inline constexpr bool is_iota_view_v<std::ranges::iota_view<W, B>> = true;

template<typename T>
concept IsIotaView = is_iota_view_v<std::remove_cvref_t<T>>;

enum class LoopControl { Continue, Break };

template<typename Container, typename Func>
void for_loop_indexing(Container&& container, Func&& func) {
    const auto size = std::size(container);
    for (size_t i = 0; i < size; ++i) {
        if (i >= size) {
            throw std::out_of_range("Index out of bounds in for_loop_indexing");
        }
        LoopControl result = func(container[i]);
        if (result == LoopControl::Break) {
            break;
        }
    }
}

template<typename Container, typename Func>
void for_loop_ranged(Container&& container, Func&& func) {
    for (auto&& element : container) {
        LoopControl result = func(element);
        if (result == LoopControl::Break) {
            break;
        }
    }
}

// falls back to indexing if UsedRangeBasedFor is false unless Container is non-owning (e.g. std::span)
// in which case you might as well use a range based for because indexing into an invalidated view is UB anyway
// this is the default for for-loops
template<bool UseRangeBasedFor = false, typename Container, typename Func>
void safe_for_loop(Container&& container, Func&& func) {
    if constexpr (UseRangeBasedFor || !OwningContainer<std::remove_cvref_t<Container>>) {
        for_loop_ranged(std::forward<Container>(container), std::forward<Func>(func));
    } else {
        if constexpr (ContiguousContainer<std::remove_cvref_t<Container>>) {
            for_loop_indexing(std::forward<Container>(container), std::forward<Func>(func));
        } else {
            static_assert(ContiguousContainer<std::remove_cvref_t<Container>>, "iterable is non-contiguous (ie a std.map) so we can't safely emit a size checked indexing for loop; it's also not a non-aliased local - make a copy to safely iterate or use for(...):unsafe");
        }
    }
}

// same behaviour as safe_for_loop but this bans any use of a non-owning view/span (except iota_view)
template<bool UseRangeBasedFor = false, typename Container, typename Func>
void safe_for_loop_strict(Container&& container, Func&& func) {
    if constexpr (UseRangeBasedFor || IsIotaView<std::remove_cvref_t<Container>>) {
        for_loop_ranged(std::forward<Container>(container), std::forward<Func>(func));
    } else {
        if constexpr (ContiguousContainer<std::remove_cvref_t<Container>> && OwningContainer<std::remove_cvref_t<Container>>) {
            for_loop_indexing(std::forward<Container>(container), std::forward<Func>(func));
        } else {
            static_assert(ContiguousContainer<std::remove_cvref_t<Container>>, "iterable is non-contiguous (ie a std.map) so we can't safely emit a size checked indexing for loop");
            static_assert(OwningContainer<std::remove_cvref_t<Container>>, "iterable is non-owning (ie a view or span) we can't emit a for-loop with 'safer' type. Don't use 'for (...):safer' or create a vec from your view with 'view | []'");
        }
    }
}

// scope resolutions whether . or :: or values that fail a lookup/validation must pass an is_simple<foo.bar.baz> check
// (only non-simple external C++ must be predeclared with a cpp(printf, std.thread) call)

template<auto T>
constexpr bool is_simple() {
    return std::is_fundamental_v<decltype(T)> ||
           std::is_enum_v<decltype(T)> ||
           std::is_arithmetic_v<decltype(T)>;
}

template<typename T>
constexpr bool is_simple() {
    return std::is_fundamental_v<T> ||
           std::is_enum_v<T> ||
           std::is_arithmetic_v<T>;
}

} // end namespace ceto

// this works but disable until unsafe blocks fully implemented
//#define CETO_BAN_RAW_DEREFERENCABLE(expr) [&]() -> decltype(auto) { static_assert(!ceto::IsRawDereferencable<std::remove_cvref_t<decltype(expr)>>); return expr; }()
#define CETO_BAN_RAW_DEREFERENCABLE(expr) (expr)


#endif // CETO_H
