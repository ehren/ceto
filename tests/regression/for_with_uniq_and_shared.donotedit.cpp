
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
 // unsafe external C++: printf, static_cast
;
struct Uniq : public ceto::object {

    decltype(0) x = 0;

        inline auto bar() -> auto {
            (this -> x) = ((this -> x) + 1);
            printf("in bar %d %p\n", this -> x, [&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(static_cast<const void *>(this))>  || (!std::is_reference_v<decltype("in bar %d %p\n")> && std::is_fundamental_v<std::remove_cvref_t<decltype("in bar %d %p\n")>> && !std::is_reference_v<decltype(this -> x)> && std::is_fundamental_v<std::remove_cvref_t<decltype(this -> x)>>)) && true)  )); return static_cast<const void *>(this); }());
            return this -> x;
            if (1) {
// Unsafe
                (this -> x) = ((this -> x) + 1);
                printf("in bar %d %p\n", this -> x, static_cast<const void *>(this));
                return this -> x;
};
        }

};

struct Shared : public ceto::shared_object, public std::enable_shared_from_this<Shared> {

    decltype(0) x = 0;

        inline auto foo() const -> auto {
            printf("foo\n");
            return 10;
        }

};

template <typename ceto__private__C1>struct Shared2 : public ceto::enable_shared_from_this_base_for_templates {

    ceto__private__C1 x;

    explicit Shared2(ceto__private__C1 x) : x(std::move(x)) {}

    Shared2() = delete;

};

    auto main() -> int {
        const auto x = 5;
        auto&& ceto__private__intermediate2 = std::vector {{1, 2, 3}};

for( auto &&  x : ceto__private__intermediate2) {
            if (1) {
// Unsafe
                printf("%d\n", x);
                x = (x + 1);
};
        }
        static_assert(std::is_const_v<decltype(x)>);
        auto lst { std::vector {{1, 2, 3}} } ;
        
for( auto &&  x : lst) {
            if (1) {
// Unsafe
                printf("%d\n", x);
                x = (x + 1);
};
        }
        
    
            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(lst)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size4 = std::size(lst);
            for (size_t ceto__private__idx3 = 0; ; ceto__private__idx3++) {
                if (std::size(lst) != ceto__private__size4) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx3 >= ceto__private__size4) {
                    break ;
                }
                 auto &&  x = lst[ceto__private__idx3];
                            if (1) {
        // Unsafe
                        printf("%d\n", x);
                        x = (x + 1);
        };

            }
            auto u { std::vector<ceto::propagate_const<std::unique_ptr<decltype(Uniq())>>>() } ;
        auto s { std::vector<ceto::propagate_const<std::shared_ptr<const decltype(Shared())>>>() } ;
        auto s2 { std::vector<ceto::propagate_const<std::shared_ptr<const decltype(Shared2{std::string {"blah"}})>>>() } ;
        auto&& ceto__private__intermediate5 = std::vector {{1, 2, 3, 4, 5}};

for(const auto& x : ceto__private__intermediate5) {
            (u).push_back(ceto::make_unique_propagate_const<Uniq>());
            (s).push_back(ceto::make_shared_propagate_const<const Shared>());
            (s2).push_back(ceto::make_shared_propagate_const<const decltype(Shared2{std::string {"blah"}})>(std::string {"blah"}));
        }
        
for( auto &  x : u) {
            printf("%d\n", /* unsafe: */ (x -> bar()));
            printf("%d\n", [&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype((*ceto::mad(/* unsafe: */ (x))).bar())>  || (!std::is_reference_v<decltype("%d\n")> && std::is_fundamental_v<std::remove_cvref_t<decltype("%d\n")>>)) && true)  )); return (*ceto::mad(/* unsafe: */ (x))).bar(); }());
        }
        int n { 0 } ; static_assert(std::is_convertible_v<decltype(0), decltype(n)>);
        
for( auto &  x : u) {
            printf("bar again: %d\n", [&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype((*ceto::mad(x)).bar())>  || (!std::is_reference_v<decltype("bar again: %d\n")> && std::is_fundamental_v<std::remove_cvref_t<decltype("bar again: %d\n")>>)) && true)  )); return (*ceto::mad(x)).bar(); }());
            n = (n + 1);
            if ((n % 2) == 0) {
                (*ceto::mad(x)).bar();
            }
        }
        
for( auto &  x : u) {
            printf("bar again again: %d\n", [&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype((*ceto::mad(x)).bar())>  || (!std::is_reference_v<decltype("bar again again: %d\n")> && std::is_fundamental_v<std::remove_cvref_t<decltype("bar again again: %d\n")>>)) && true)  )); return (*ceto::mad(x)).bar(); }());
        }
        auto v { std::vector {ceto::make_shared_propagate_const<Shared>()} } ;
        auto v2 { std::vector {ceto::make_shared_propagate_const<const Shared>()} } ;
        
    
            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(s)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size7 = std::size(s);
            for (size_t ceto__private__idx6 = 0; ; ceto__private__idx6++) {
                if (std::size(s) != ceto__private__size7) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx6 >= ceto__private__size7) {
                    break ;
                }
                const auto i = s[ceto__private__idx6];
                            (*ceto::mad(i)).foo();
                    (v2).push_back([&]() -> decltype(auto) { static_assert((((!std::is_reference_v<decltype(i)> ) && true)  || ceto::IsContainer<std::remove_cvref_t<decltype(v2)>>)); return i; }());

            }
            
    
            static_assert(ceto::ContiguousContainer<std::remove_cvref_t<decltype(v2)>>, "this loop requires a contiguous container (e.g. std.vector is contiguous, std.map is not)");
    
            size_t ceto__private__size9 = std::size(v2);
            for (size_t ceto__private__idx8 = 0; ; ceto__private__idx8++) {
                if (std::size(v2) != ceto__private__size9) {
                    std::cerr << "Container size changed during iteration: " << __FILE__ << " line: "<< __LINE__ << "\n";
                    std::terminate();
                }
                if (ceto__private__idx8 >= ceto__private__size9) {
                    break ;
                }
                const auto vv2 = v2[ceto__private__idx8];
                            (*ceto::mad(vv2)).foo();

            }
            const auto s1 = ceto::make_shared_propagate_const<Shared>();
        
for( auto  v1 : v) {
            (*ceto::mad(v1)).x = 55;
            std::cout << "v:" << (*ceto::mad(v1)).foo();
        }
    }

