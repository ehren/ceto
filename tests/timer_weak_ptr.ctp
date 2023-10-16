

cpp'
#include <mutex>
'

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

    _thread: std.thread = {}

    def (start: mut:
        w: weak:Delegate = self._delegate

        self._thread = std.thread(lambda(:
            while (true:
                std.this_thread.sleep_for(std.chrono.seconds(1))
                if ((s = w.lock()):
                    s.action()
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
    