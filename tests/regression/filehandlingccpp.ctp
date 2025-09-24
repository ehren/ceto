# Test Output: hello world

include <fstream>
include <sstream>

unsafe.extern(fopen, fclose, fprintf, std.ifstream, std.stringstream)

def (main:
    fp = fopen("file.txt", "w+")
    fprintf(fp, "hello %s", "world\n")
    fclose(fp)
    fp2 = fopen("file.txt", "r")
    fclose(fp2)
    
    t = std.ifstream(c"file.txt")
    buffer : mut = std.stringstream()
    buffer << t.rdbuf()
    s = buffer.str()
    std.cout << s << "\n"
)
    
