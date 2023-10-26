# Test Output: 0121019

# https://stackoverflow.com/questions/571394/how-to-find-out-if-an-item-is-present-in-a-stdvector
def (contains, container, element: const:typename:std.remove_reference_t<decltype(container)>::value_type:ref:
    return std.find(container.begin(), container.end(), element) != container.end()
)

def (main:
    l = [0, 1, 2, 10, 19, 20]
    for (i in range(20):
        if (contains(l, i):
            std.cout << i
        )
    )
)
    
