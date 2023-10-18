# Test Output: hi53
# Test Output: 2

def (main:
    x:int:mut
    x = 0
    (static_cast<void>)(x)  # silence unused variable warning
    
    f = lambda (y:const:char:ptr, z:int:mut:
        std: using: namespace  # variable declaration 'like'
        t : typedef : int
        w : t = 3
        cout << y << z << w << endl
        z = 2  # unrelated test that lambda params treated as defs in 'find_defs'.
        cout << z << endl
        void()
    )
    
    f("hi".c_str(), 5)
)
    