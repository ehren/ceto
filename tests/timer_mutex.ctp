# Test Output: action
# Test Output: action
# Test Output: action
# Test Output: Delegate destruct
# Test Output: Timer destruct

include <mutex>

class (Delegate:
    def (action:
        std.cout << "action\n"
    )

    def (destruct:
        std.cout << "Delegate destruct\n"
    )
)

class (Timer:
    _delegate: Delegate

    _delegate_mutex = std.mutex()
    _thread: std.thread = {}

    def (start: mut:
        self._thread = std.thread(lambda(:
            # here we're capturing self by value which is safe in multithreaded
            # code (different shared_ptr instances), otoh we're accessing the 
            # same shared_ptr<Delegate> instance across two threads which requires synchronization
            while (true:
                std.this_thread.sleep_for(std.chrono.seconds(1))
                guard = std.lock_guard<std.mutex>(self._delegate_mutex)
                if (self._delegate:
                    self._delegate.action()
                else:
                    break
                )
            )
        ))
    )

    def (join: mut:
        self._thread.join()
    )

    def (clear_delegate: mut:
        guard = std.lock_guard<std.mutex>(self._delegate_mutex)
        self._delegate = None
    )

    def (destruct:
        std.cout << "Timer destruct\n"
    )
)

def (main:
    timer: mut = Timer(Delegate())
    timer.start()

    std.literals: using:namespace
    std.this_thread.sleep_for(3.5s)

    timer.clear_delegate()
    timer.join()
)
    