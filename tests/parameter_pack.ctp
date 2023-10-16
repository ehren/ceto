
    
# Example from https://en.cppreference.com/w/cpp/language/parameter_pack
# void tprintf(const char* format) // base function
# {
#     std::cout << format;
# }
#  
# template<typename T, typename... Targs>
# void tprintf(const char* format, T value, Targs... Fargs) // recursive variadic function
# {
#     for (; *format != '\0'; format++)
#     {
#         if (*format == '%')
#         {
#             std::cout << value;
#             tprintf(format + 1, Fargs...); // recursive call
#             return;
#         }
#         std::cout << *format;
#     }
# }
#  
# int main()
# {
#     tprintf("% world% %\n", "Hello", '!', 123);
# }
    
def (tprintf, format: const:char:ptr: # base function
    std.cout << format
)
    
def (tprintf: template<typename:T, typename:...:Targs>,  # recursive variadic function
      format: const:char:ptr, 
       value: T, 
       Fargs: Targs:...:
      
    while (*format != c"".unsafe_at(0):  # TODO maybe char"%" for char literal
        if (*format == c"%".unsafe_at(0):
            std.cout << value
            tprintf(format + 1, Fargs...) # recursive call
            return
        )
        std.cout << *format
        format = format + 1
    )
)
    
def (main:
    tprintf(c"% world% %\n", c"Hello", c"!".unsafe_at(0), 123);
)
    