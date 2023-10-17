# Test Output: 12341234555

def (byref, v : [int]:  # pass by const ref
    static_assert(std.is_reference_v<decltype(v)>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(v)>>)
    static_assert(std.is_same_v<decltype(v), const:std.vector<int>:ref>)
)

def (byconstval, v : const:[int]:  # pass by const val (TODO maybe a bit of a performance gotcha - should be an error or maybe still const ref)
    static_assert(not std.is_reference_v<decltype(v)>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(v)>>)
    static_assert(std.is_same_v<decltype(v), const:std.vector<int>>)
)

def (byref2, v : const:[int]:ref:  # pass by const ref
    static_assert(std.is_reference_v<decltype(v)>)
    static_assert(std.is_const_v<std.remove_reference_t<decltype(v)>>)
    static_assert(std.is_same_v<decltype(v), const:std.vector<int>:ref>)
)

def (byval, v : mut:[int]:  # pass by val
    static_assert(not std.is_reference_v<decltype(v)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(v)>>)
    static_assert(std.is_same_v<decltype(v), std.vector<int>>)
    # v.append(5)  # TODO
    v.push_back(5)
    return v
)

def (byval4, v : [int]:mut:  # pass by val
    static_assert(not std.is_reference_v<decltype(v)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(v)>>)
    static_assert(std.is_same_v<decltype(v), std.vector<int>>)
    # v.append(5)  # TODO
    v.push_back(5)
    return v
)

def (by_mut_ref, v : mut:[int]:ref:  # pass by non-const ref
    static_assert(std.is_reference_v<decltype(v)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(v)>>)
    static_assert(std.is_same_v<decltype(v), std.vector<int>:ref>)
    # v.append(5)  # TODO
    v.push_back(5)
    return v
)

def (by_mut_ref2, v : [int]:ref:mut:  # pass by non-const ref
    static_assert(std.is_reference_v<decltype(v)>)
    static_assert(not std.is_const_v<std.remove_reference_t<decltype(v)>>)
    static_assert(std.is_same_v<decltype(v), std.vector<int>:ref>)
    # v.append(5)  # TODO
    v.push_back(5)
    return v
)

# TODO
# def (byval2, v : mut:[int] = [1,2]:
#     static_assert(not std.is_reference_v<decltype(v)>)
#     static_assert(not std.is_const_v<std.remove_reference_t<decltype(v)>>)
#     static_assert(std.is_same_v<decltype(v), std.vector<int>>)
#     # v.append(5)  # TODO
#     v.push_back(5)
#     return v
# )

# def (byval3, v : mut = 5:
#     pass
# )

def (main:
    v : mut : [int] = [1, 2, 3]
    v.append(4)
    for (v in v:  # shadowing test
        std.cout << v
    )
    byref(v)
    by_mut_ref(v)
    by_mut_ref2(v)
    for (v in byval(v):
        std.cout << v
    )
    # for (v in byval2():
    #     std.cout << v
    # )
)
    