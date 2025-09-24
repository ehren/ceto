
    
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
    
def (tprintf, format: const:char:pointer: # base function
    std.cout << format
)
    
def (tprintf: template<typename:T, typename:...:Targs>,  # recursive variadic function
      format: const:char:pointer, 
       value: T, 
       Fargs: Targs:...:
      
    while (*format != char'\0':
        if (*format == char'%':
            std.cout << value
            tprintf(format + 1, Fargs...) # recursive call
            return
        )
        std.cout << *format
        format = format + 1
    )
)
    
def (main:
    tprintf("% world% %\n", "Hello", char"!", 123);
)
    
