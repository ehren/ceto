
#include <string>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <sstream>
#include <functional>
#include <cassert>
#include <compare> // for <=>
#include <thread>
#include <optional>

//#include <concepts>
//#include <ranges>
//#include <numeric>


#include "ceto.h"


#include <thread>
;
struct Delegate : public ceto::shared_object, public std::enable_shared_from_this<Delegate> {

        inline auto action() const -> void {
            std::cout << "action\n";
        }

        ~Delegate() {
            std::cout << "Delegate destruct\n";
        }

};

struct Timer : public ceto::shared_object, public std::enable_shared_from_this<Timer> {

    std::shared_ptr<const Delegate> _delegate;

    std::thread _thread = {};

        inline auto start() -> void {
            const std::weak_ptr<const Delegate> w = (this -> _delegate); static_assert(ceto::is_non_aggregate_init_and_if_convertible_then_non_narrowing_v<decltype((this -> _delegate)), std::remove_cvref_t<decltype(w)>>);
            (this -> _thread) = std::thread([w = ceto::default_capture(w)]() {
                    while (true) {                        std::this_thread::sleep_for(std::chrono::seconds(1));
                        if (const auto s = ceto::mado(w)->lock()) {
                            ceto::mado(s)->action();
                        } else {
                            break;
                        }
                    }
                    return;
                    });
        }

        inline auto join() -> void {
            ceto::mado(this -> _thread)->join();
        }

        inline auto clear_delegate() -> void {
            (this -> _delegate) = nullptr;
        }

        ~Timer() {
            std::cout << "Timer destruct\n";
        }

    explicit Timer(std::shared_ptr<const Delegate> _delegate) : _delegate(std::move(_delegate)) {}

    Timer() = delete;

};

    auto main() -> int {
        auto timer { std::make_shared<decltype(Timer{std::make_shared<const decltype(Delegate())>()})>(std::make_shared<const decltype(Delegate())>()) } ;
        ceto::mado(timer)->start();
        using namespace std::literals;
        std::this_thread::sleep_for(3.5s);
        ceto::mado(timer)->clear_delegate();
        ceto::mado(timer)->join();
    }

