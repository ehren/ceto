# Test Output: hi
# Test Output:
# Test Output:
# Test Output: end

def (main:
    std.cout  : using  # this should be the encouraged syntax
    std::endl : using  # but for additional C++ compat
    
    # However, regarding implicit namespaces e.g. std.cout vs std::endl
    # is there a precedence mismatch problem with the tighter binding scope resolution operator in C++? (when our parse tree is built using '.'). Can't think of problematic example 
    
    cout << "hi" << endl << std::endl << std.endl << "end"
)
    