# Test Output: hello world

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
    