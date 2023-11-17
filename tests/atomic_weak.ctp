# https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2014/n4162.pdf
# atomic_weak_ptr<X> p_last;
#
# void use( const shared_ptr<X>& x ) {
#     do_something_with( *x );
#     p_last = x; // remember last X seen
# }

include <atomic>
include <ranges>


class (Task:
    _id : int
    
    def (id:
        return self._id
    )

    def (action:
        std.cout << "action: " << self._id << "\n"
        std.this_thread.sleep_for(std.chrono.milliseconds(self._id * 100))
        std.cout << "finished: " << self._id << "\n"
    )
    
    def (destruct:
        std.cout << "Task " << self._id << " dead\n"
    )
)
    
class (Executor:
    last_submitted : std.atomic<weak:Task> = {}
    last_finished : std.atomic<weak:Task> = {}

    def (do_something: mut, task: Task:
        self.last_submitted = task
        task.action()
        self.last_finished = task
    )

    # doing a bunch of stuff that can throw in a destructor is usually not the best idea
    # (fine for testsuite)
    def (destruct:
        std.cout << "Last task submitted: " << if ((strong = self.last_submitted.load().lock()): 
            std.to_string(strong.id())
        else:
            s"Last submitted task not found"
        ) << "\nLast task finished: " << if ((strong = self.last_finished.load().lock()):
            std.to_string(strong.id())
        else:
            s"Last finished task not found"
        ) << "\n"
    )
)

def (launch, tasks : [Task]:
    executor : mut = Executor()
    threads: mut:[std.thread] = []
    # threads: mut = []  # TODO should work (we don't handle the captured var 'task' well when building the type upon encountering the lambda)
    
    for (task in tasks:
        threads.append(std.thread(lambda(executor.do_something(task))))
    )
    
    for (thread: mut:auto:rref in threads:
        thread.join()
    )
)

def (main:
    tasks : mut = []
    
    for (i in std.ranges.iota_view(0, 10):
        tasks.append(Task(i))
    )
    
    launch(tasks)
)
