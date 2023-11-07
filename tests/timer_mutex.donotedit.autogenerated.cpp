
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

#include <mutex>
;
struct Delegate : public ceto::shared_object, public std::enable_shared_from_this<Delegate> {

        inline auto action() const -> void {
            std::cout << std::string {"action\n"};
        }

        ~Delegate() {
            std::cout << std::string {"Delegate destruct\n"};
        }

};

struct Timer : public ceto::shared_object, public std::enable_shared_from_this<Timer> {

    std::shared_ptr<const Delegate> _delegate;

    std::remove_cvref_t<decltype(std::mutex())> _delegate_mutex = std::mutex();

    std::thread _thread = {};

        inline auto start() -> void {
            const auto self = ceto::shared_from(this);
            (this -> _thread) = std::thread([self = ceto::default_capture(self)]() {
while (true) {                        std::this_thread::sleep_for(std::chrono::seconds(1));
                        const auto guard = std::lock_guard<std::mutex>(ceto::mado(self)->_delegate_mutex);
if (ceto::mado(self)->_delegate) {
                            ceto::mado(ceto::mado(self)->_delegate)->action();
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
            const auto guard = std::lock_guard<std::mutex>(this -> _delegate_mutex);
            (this -> _delegate) = nullptr;
        }

        ~Timer() {
            std::cout << std::string {"Timer destruct\n"};
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

