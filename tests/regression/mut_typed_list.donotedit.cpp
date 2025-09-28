
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
    inline auto byref(const std::vector<int>&  v) -> void {
        static_assert(std::is_reference_v<decltype(v)>);
        static_assert(std::is_const_v<std::remove_reference_t<decltype(v)>>);
        static_assert(std::is_same_v<decltype(v),const std::vector<int> &>);
    }

    inline auto byconstval( const std::vector<int>  v) -> void {
        static_assert(!std::is_reference_v<decltype(v)>);
        static_assert(std::is_const_v<std::remove_reference_t<decltype(v)>>);
        static_assert(std::is_same_v<decltype(v),const std::vector<int>>);
    }

    inline auto byref2( const std::vector<int> &  v) -> void {
        static_assert(std::is_reference_v<decltype(v)>);
        static_assert(std::is_const_v<std::remove_reference_t<decltype(v)>>);
        static_assert(std::is_same_v<decltype(v),const std::vector<int> &>);
    }

    inline auto byval( std::vector<int>  v) -> auto {
        static_assert(!std::is_reference_v<decltype(v)>);
        static_assert(!std::is_const_v<std::remove_reference_t<decltype(v)>>);
        static_assert(std::is_same_v<decltype(v),std::vector<int>>);
        (*ceto::mad(v)).push_back(5);
        return v;
    }

    inline auto byval4( std::vector<int>  v) -> auto {
        static_assert(!std::is_reference_v<decltype(v)>);
        static_assert(!std::is_const_v<std::remove_reference_t<decltype(v)>>);
        static_assert(std::is_same_v<decltype(v),std::vector<int>>);
        (*ceto::mad(v)).push_back(5);
        return v;
    }

    inline auto by_mut_ref( std::vector<int> &  v) -> auto {
        static_assert(std::is_reference_v<decltype(v)>);
        static_assert(!std::is_const_v<std::remove_reference_t<decltype(v)>>);
        static_assert(std::is_same_v<decltype(v),std::vector<int> &>);
        (*ceto::mad(v)).push_back(5);
        return v;
    }

    inline auto by_mut_ref2( std::vector<int> &  v) -> auto {
        static_assert(std::is_reference_v<decltype(v)>);
        static_assert(!std::is_const_v<std::remove_reference_t<decltype(v)>>);
        static_assert(std::is_same_v<decltype(v),std::vector<int> &>);
        (*ceto::mad(v)).push_back(5);
        return v;
    }

    auto main() -> int {
        std::vector<int> v = std::vector<int>{1, 2, 3}; static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype(std::vector<int>{1, 2, 3}), std::remove_cvref_t<decltype(v)>>);
        (v).push_back(4);
        
    
            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(v)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size2 = std::size(v);
            for (size_t ceto__private__idx1 = 0; ; ceto__private__idx1++) {
                if (std::size(v) != ceto__private__size2) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx1 >= ceto__private__size2) {
                    break ;
                }
                const auto v = v[ceto__private__idx1];
                            std::cout << v;

            }
            byref(v);
        by_mut_ref(v);
        by_mut_ref2(v);
        ceto::safe_for_loop<!std::is_reference_v<decltype(byval(v))> && ceto::OwningContainer<std::remove_cvref_t<decltype(byval(v))>>>(byval(v), [&](auto &&ceto__private__lambda_param3) -> ceto::LoopControl {
    const auto v = ceto__private__lambda_param3;
            std::cout << v;
    return ceto::LoopControl::Continue;
});    }

