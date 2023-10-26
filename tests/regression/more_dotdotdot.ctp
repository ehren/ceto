
    
# https://en.cppreference.com/w/cpp/language/parameter_pack
# template<class... Types>
# struct count
# {
#     static const std::size_t value = sizeof...(Types);
# };

# no explicit template class support yet

def (count: template<typename:...:Types>:
    return (sizeof...)(Types)   # note extra parethese to "call" non-atom
)

def (main:
    std::cout << count<int, float, char>()
)
    