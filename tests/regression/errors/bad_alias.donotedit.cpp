
#include "ceto.h"

;

;

;

;

;

;

;

;

;

;

;

;

;

;
#include "ceto_private_listcomp.donotedit.h"
;
#include "ceto_private_boundscheck.donotedit.h"
;
#include "ceto_private_convenience.donotedit.h"
;
#include "ceto_private_append_to_pushback.donotedit.h"
;
#include <functional>
;
struct Foo : public ceto::shared_object, public std::enable_shared_from_this<Foo> {

    std::vector<int> vec;

        template <typename ceto__private__T11>
auto ok_method(const ceto__private__T11& x) -> void {
            (*ceto::mad(this -> vec)).push_back(42);
            std::cout << x;
        }

    explicit Foo(std::vector<int> vec) : vec(std::move(vec)) {}

    Foo() = delete;

};

template <typename ceto__private__C2>struct FooStruct : public ceto::object {

    ceto__private__C2 foo;

    explicit FooStruct(ceto__private__C2 foo) : foo(std::move(foo)) {}

    FooStruct() = delete;

};

    template <typename ceto__private__T13>
auto ok(const ceto__private__T13& x,  auto  foo) -> void {
        ceto::append_or_push_back((*ceto::mad(foo)).vec, 1);
        std::cout << x;
    }

    template <typename ceto__private__T14, typename ceto__private__T25>
auto ok2(const ceto__private__T14& x, const ceto__private__T25& foo) -> void {
        auto m { foo } ;
        ceto::append_or_push_back((*ceto::mad(m)).vec, 1);
        std::cout << x;
    }

    template <typename ceto__private__T16, typename ceto__private__T27>
auto ok3(const ceto__private__T16& x, const ceto__private__T27& foo_struct) -> void {
        auto fm { foo_struct } ;
        auto m { (*ceto::mad(fm)).foo } ;
        ceto::append_or_push_back((*ceto::mad(m)).vec, 1);
        std::cout << x;
    }

    template <typename ceto__private__T18, typename ceto__private__T29>
auto good4(const ceto__private__T18& v, const ceto__private__T29& foo_struct) -> void {
        auto m { (*ceto::mad(foo_struct)).foo } ;
        ceto::append_or_push_back((*ceto::mad(m)).vec, 1);
        std::cout << ceto::bounds_check(v, 0);
    }

    template <typename ceto__private__T110>
auto ok5(const ceto__private__T110& x,  auto &  v) -> void {
        ceto::append_or_push_back(v, 1);
        std::cout << x;
    }

    template <typename ceto__private__T111>
auto bad6(const ceto__private__T111& v,  auto &  v2) -> void {
        
    
            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(v)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size13 = std::size(v);
            for (size_t ceto__private__idx12 = 0; ; ceto__private__idx12++) {
                if (std::size(v) != ceto__private__size13) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx12 >= ceto__private__size13) {
                    break ;
                }
                 auto &  x = v[ceto__private__idx12];
                            ok5(/* unsafe: */ (x), v2);
                    break;

            }
        }

    template <typename ceto__private__T114>
auto bad7(const ceto__private__T114& f,  auto &  v2) -> void {
        
            auto&& ceto__private__intermediate15 = (*ceto::mad(f)).vec;

            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate15)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size17 = std::size(ceto__private__intermediate15);
            for (size_t ceto__private__idx16 = 0; ; ceto__private__idx16++) {
                if (std::size(ceto__private__intermediate15) != ceto__private__size17) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx16 >= ceto__private__size17) {
                    break ;
                }
                 const auto &  x = ceto__private__intermediate15[ceto__private__idx16];
                            ceto::append_or_push_back(v2, 1);
                    /* unsafe: */ (std::cout << x);
                    break;

            }
        }

    template <typename ceto__private__T118>
auto bad8(const ceto__private__T118& f,  auto  f2) -> void {
        
            auto&& ceto__private__intermediate19 = (*ceto::mad(f)).vec;

            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate19)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size21 = std::size(ceto__private__intermediate19);
            for (size_t ceto__private__idx20 = 0; ; ceto__private__idx20++) {
                if (std::size(ceto__private__intermediate19) != ceto__private__size21) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx20 >= ceto__private__size21) {
                    break ;
                }
                 const auto &  x = ceto__private__intermediate19[ceto__private__idx20];
                            ceto::append_or_push_back((*ceto::mad(f2)).vec, 1);
                    if (1) {
        // Unsafe
                        std::cout << x;
        };
                    break;

            }
        }

    template <typename ceto__private__T122>
auto good9(const ceto__private__T122& f,  auto  f2) -> void {
        
            auto&& ceto__private__intermediate23 = (*ceto::mad(f)).vec;

            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate23)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size25 = std::size(ceto__private__intermediate23);
            for (size_t ceto__private__idx24 = 0; ; ceto__private__idx24++) {
                if (std::size(ceto__private__intermediate23) != ceto__private__size25) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx24 >= ceto__private__size25) {
                    break ;
                }
                const auto x = ceto__private__intermediate23[ceto__private__idx24];
                            ceto::append_or_push_back((*ceto::mad(f2)).vec, 1);
                    std::cout << x;
                    break;

            }
        }

    inline auto good10( auto  f,  auto  f2) -> void {
        
            auto&& ceto__private__intermediate26 = (*ceto::mad(f)).vec;

            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate26)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size28 = std::size(ceto__private__intermediate26);
            for (size_t ceto__private__idx27 = 0; ; ceto__private__idx27++) {
                if (std::size(ceto__private__intermediate26) != ceto__private__size28) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx27 >= ceto__private__size28) {
                    break ;
                }
                const auto x = ceto__private__intermediate26[ceto__private__idx27];
                            ceto::append_or_push_back((*ceto::mad(f2)).vec, 1);
                    std::cout << x;
                    break;

            }
        }

    inline auto mutates( auto  f) -> void {
        ceto::append_or_push_back((*ceto::mad(f)).vec, 42);
    }

struct HoldsFunc : public ceto::shared_object, public std::enable_shared_from_this<HoldsFunc> {

    std::function<void(const int &)> func;

    explicit HoldsFunc(std::function<void(const int &)> func) : func(func) {}

    HoldsFunc() = delete;

};

    auto main() -> int {
        auto vec { std::vector {{1, 2, 3, 4}} } ;
        auto f { ceto::make_shared_propagate_const<Foo>(vec) } ;
        auto s { FooStruct{f} } ;
        ok([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(ceto::bounds_check((*ceto::mad(f)).vec, 0))>  || (!std::is_reference_v<decltype(f)> && std::is_fundamental_v<std::remove_cvref_t<decltype(f)>>)) && true)  )); return ceto::bounds_check((*ceto::mad(f)).vec, 0); }(), f);
        ok2([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(ceto::bounds_check((*ceto::mad(f)).vec, 0))>  || (!std::is_reference_v<decltype(f)> && std::is_fundamental_v<std::remove_cvref_t<decltype(f)>>)) && true)  )); return ceto::bounds_check((*ceto::mad(f)).vec, 0); }(), f);
        ok3([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(ceto::bounds_check((*ceto::mad(f)).vec, 0))>  || (!std::is_reference_v<decltype(s)> && std::is_fundamental_v<std::remove_cvref_t<decltype(s)>>)) && true)  )); return ceto::bounds_check((*ceto::mad(f)).vec, 0); }(), s);
        good4((*ceto::mad(f)).vec, s);
        ok5([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(ceto::bounds_check((*ceto::mad(f)).vec, 0))>  || (!std::is_reference_v<decltype((*ceto::mad(f)).vec)> && std::is_fundamental_v<std::remove_cvref_t<decltype((*ceto::mad(f)).vec)>>)) && true)  )); return ceto::bounds_check((*ceto::mad(f)).vec, 0); }(), (*ceto::mad(f)).vec);
        bad6((*ceto::mad(f)).vec, (*ceto::mad(f)).vec);
        (*ceto::mad(f)).ok_method([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(ceto::bounds_check((*ceto::mad(f)).vec, 0))> ) && true)  || ceto::IsContainer<std::remove_cvref_t<decltype(f)>>)); return ceto::bounds_check((*ceto::mad(f)).vec, 0); }());
        bad7(f, (*ceto::mad(f)).vec);
        bad8(f, f);
        good9(f, f);
        good10(f, f);
        const auto ok_lambda = [f = ceto::default_capture(f)](const auto &x) {
                auto f_m { f } ;
                return ceto::append_or_push_back((*ceto::mad(f_m)).vec, 42);
                };
        ok_lambda([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(ceto::bounds_check((*ceto::mad(f)).vec, 0))> ) && ceto::IsStateless<std::remove_cvref_t<decltype(ok_lambda)>>) || ceto::IsStateless<std::remove_cvref_t<decltype(ok_lambda)>> )); return ceto::bounds_check((*ceto::mad(f)).vec, 0); }());
        const auto ok_lambda2 = [f = ceto::default_capture(f)](const auto &x) {
                return mutates(f);
                };
        ok_lambda2([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(ceto::bounds_check((*ceto::mad(f)).vec, 0))> ) && ceto::IsStateless<std::remove_cvref_t<decltype(ok_lambda2)>>) || ceto::IsStateless<std::remove_cvref_t<decltype(ok_lambda2)>> )); return ceto::bounds_check((*ceto::mad(f)).vec, 0); }());
        const auto ok_lambda3 = [](const auto &x, const auto &f) {
                return mutates(f);
                };
        ok_lambda3([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(ceto::bounds_check((*ceto::mad(f)).vec, 0))>  || (!std::is_reference_v<decltype(f)> && std::is_fundamental_v<std::remove_cvref_t<decltype(f)>>)) && ceto::IsStateless<std::remove_cvref_t<decltype(ok_lambda3)>>)  )); return ceto::bounds_check((*ceto::mad(f)).vec, 0); }(), f);
        const auto has_ok_lambda_member1 = ceto::make_shared_propagate_const<const HoldsFunc>([f = ceto::default_capture(f)](const auto &x) {
                return mutates(f);
                });
        const auto ok_lambda5 = []( auto  x,  auto  f) {
                return mutates(f);
                };
        const auto val = ceto::bounds_check((*ceto::mad(f)).vec, 0);
        (*ceto::mad(has_ok_lambda_member1)).func(val);
        (*ceto::mad(has_ok_lambda_member1)).func([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(ceto::bounds_check((*ceto::mad(f)).vec, 0))> ) && true)  || ceto::IsContainer<std::remove_cvref_t<decltype(has_ok_lambda_member1)>>)); return ceto::bounds_check((*ceto::mad(f)).vec, 0); }());
        ok_lambda5(val, f);
        ok_lambda5([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(ceto::bounds_check((*ceto::mad(f)).vec, 0))>  || (!std::is_reference_v<decltype(f)> && std::is_fundamental_v<std::remove_cvref_t<decltype(f)>>)) && ceto::IsStateless<std::remove_cvref_t<decltype(ok_lambda5)>>)  )); return ceto::bounds_check((*ceto::mad(f)).vec, 0); }(), f);
        const auto ok_func_member_copy = (*ceto::mad(has_ok_lambda_member1)).func;
        ok_func_member_copy([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(ceto::bounds_check((*ceto::mad(f)).vec, 0))> ) && ceto::IsStateless<std::remove_cvref_t<decltype(ok_func_member_copy)>>) || ceto::IsStateless<std::remove_cvref_t<decltype(ok_func_member_copy)>> )); return ceto::bounds_check((*ceto::mad(f)).vec, 0); }());
        const auto ok_lambda_like_ok5 = [](const auto &x,  auto &  v) {
                return ceto::append_or_push_back(v, 1);
                };
        ok_lambda_like_ok5([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(ceto::bounds_check((*ceto::mad(f)).vec, 0))>  || (!std::is_reference_v<decltype((*ceto::mad(f)).vec)> && std::is_fundamental_v<std::remove_cvref_t<decltype((*ceto::mad(f)).vec)>>)) && ceto::IsStateless<std::remove_cvref_t<decltype(ok_lambda_like_ok5)>>)  )); return ceto::bounds_check((*ceto::mad(f)).vec, 0); }(), (*ceto::mad(f)).vec);
        const auto bad_lambda_like_bad8 = [](const auto &f,  auto  f2) {
                
                    auto&& ceto__private__intermediate29 = (*ceto::mad(f)).vec;

                    static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(ceto__private__intermediate29)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
                    size_t ceto__private__size31 = std::size(ceto__private__intermediate29);
                    for (size_t ceto__private__idx30 = 0; ; ceto__private__idx30++) {
                        if (std::size(ceto__private__intermediate29) != ceto__private__size31) {
                            std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                            std::terminate();
                        }
                        if (ceto__private__idx30 >= ceto__private__size31) {
                            break ;
                        }
                         const auto &  x = ceto__private__intermediate29[ceto__private__idx30];
                                            ceto::append_or_push_back((*ceto::mad(f2)).vec, 1);
                                    std::cout << /* unsafe: */ (x);
                                    break;

                    }
                    return;
                };
        bad_lambda_like_bad8(f, f);
    }

