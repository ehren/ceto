
    
# from https://herbsutter.com/2013/05/09/gotw-1-solution/

# template<typename T, typename ...Args>
# void forwarder( Args&&... args ) {
#     // ...
#     T local = { std::forward<Args>(args)... };
#     // ...
# }

def (forwarder: template<typename:T, typename:...:Args>,
          args: mut:Args:rref:...:  # TODO const:rref makes no sense so don't require 'mut' in this case? (not requiring 'mut' would be similar to not requiring 'mut' for a 'unique' param)
    local: T = { std.forward<Args>(args)... }
)

def (main:
    # from article:  "forwarder<vector<int>> ( 1, 2, 3, 4 ); // ok because of {}
    forwarder<std.vector<int>> (1, 2, 3, 4)
)
    