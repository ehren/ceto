
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

#include <atomic>
;
#include <ranges>
;
struct Task : ceto::shared_object {

    int _id;

        inline auto id() const -> auto {
            return (this -> _id);
        }

        inline auto action() const -> void {
            ((std::cout << std::string {"action: "}) << (this -> _id)) << std::string {"\n"};
            std::this_thread::sleep_for(std::chrono::milliseconds((this -> _id) * 100));
            ((std::cout << std::string {"finished: "}) << (this -> _id)) << std::string {"\n"};
        }

        ~Task() {
            ((std::cout << std::string {"Task "}) << (this -> _id)) << std::string {" dead\n"};
        }

    explicit Task(int _id) : _id(_id) {}

    Task() = delete;

};

struct Executor : ceto::shared_object {

    std::atomic<std::weak_ptr<const Task>> last_submitted = {};

    std::atomic<std::weak_ptr<const Task>> last_finished = {};

        inline auto do_something(const std::shared_ptr<const Task>&  task) -> void {
            (this -> last_submitted) = task;
            ceto::mado(task)->action();
            (this -> last_finished) = task;
        }

        ~Executor() {
            ((((std::cout << std::string {"Last task submitted: "}) << [&]() {if (const auto strong = ceto::mado(ceto::mado(this -> last_submitted)->load())->lock()) {
                return std::to_string(ceto::mado(strong)->id());
            } else {
                return std::string {"Last submitted task not found"};
            }}()
) << std::string {"\nLast task finished: "}) << [&]() {if (const auto strong = ceto::mado(ceto::mado(this -> last_finished)->load())->lock()) {
                return std::to_string(ceto::mado(strong)->id());
            } else {
                return std::string {"Last finished task not found"};
            }}()
) << std::string {"\n"};
        }

};

    inline auto launch(const std::vector<std::shared_ptr<const Task>>&  tasks) -> auto {
        auto executor { std::make_shared<decltype(Executor())>() } ;
        auto threads { std::vector<std::thread>{} } ;
        for(const auto& task : tasks) {
            ceto::mad(threads)->push_back(std::thread([task = ceto::default_capture(task), executor = ceto::default_capture(executor)]() {
                    if constexpr (!std::is_void_v<decltype(ceto::mado(executor)->do_something(task))>) { return ceto::mado(executor)->do_something(task); } else { static_cast<void>(ceto::mado(executor)->do_something(task)); };
                    }));
        }
        for( auto &&  thread : threads) {
            ceto::mado(thread)->join();
        }
    }

    auto main() -> int {
        auto tasks { std::vector<std::shared_ptr<const decltype(Task{std::declval<std::ranges::range_value_t<decltype(std::ranges::iota_view(0, 10))>>()})>>() } ;
        for(const auto& i : std::ranges::iota_view(0, 10)) {
            ceto::mad(tasks)->push_back(std::make_shared<const decltype(Task{i})>(i));
        }
        launch(tasks);
    }

