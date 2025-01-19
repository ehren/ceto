# Test Output 5aaabbb

namespace(blah:
    def (append, x:
        static_cast<void>(x)
    )
)

def (calls_generic_append, vec, element:
    vec_copy: mut = vec
    vec_copy.append(element)
    return vec_copy
)

def (main:
    blah.append(1)  # make sure we haven't broken implicit scope resolution in this case

    std.cout << calls_generic_append([1, 2, 3, 4], 5)[4]  # calls std::vector::push_back

    std.cout << calls_generic_append("aaa"s, "bbb")  # calls std::string::append

    # Note: if you have generic code that differentiates std::string vs std::vector by whether you can call .append vs .push_back it's broken. OTOH generic code calling push_back on both std::vector and std::string, while still possible, is discouraged by the convention of calling append for vectors in idiomatic code!
)
