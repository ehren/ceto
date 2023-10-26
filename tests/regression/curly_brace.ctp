

cpp'
#include <array>
'

def (main:
    l : std.vector<std.vector<int>> = {{1}, {1,2,3}}
    l2 : std.vector<std.vector<int>> = {{1,2}}
    l3 : std.vector<std.vector<int>> = {{1}}
    l4 : std.vector<std.vector<int>> = {}


    a : std.vector<int> = {5,2}
    a2 : std.vector<std.vector<int>> = {l}  # confusing?
    a3 : std.vector<std.vector<int>> = l
    a4 : std.vector<std.vector<int>> = {{l}}

    # implement python style chained comparison?
    assert(2 == a.size() and 2 == a2.size() and 2 == a3.size() and 2 == a4.size())

    # TODO:
    # for (l in [l, l2, l3]:  # hang: "are we handling this correctly (def args)" (see self assign hang fix)
    #     for (k in l:
    #         std.cout << k
    #     )
    # )

    # this broke with previous insertion of declval:
    # for(auto && ll : std::vector<decltype(std::declval<std::vector<std::vector<int>>>())>{l, l2, l3}) {

    # now works:
    for (ll in [l, l2, l3, l4, a2]:
        for (li in ll:
            for (lk in li:
                std.cout << lk
            )
        )
    )

    std.cout << l3[0][0]

    arr: std.array<int, 4> = {{1, 2, 3, 4}}
    arr2: std.array<int, 2> = {1, 2}

    arr3: std::array<std::array<int, 3>, 2> = { { { {1, 2, 3} }, { { 4, 5, 6} } } }
    arr4: std::array<std::array<int, 3>, 2> = { { {1, 2, 3} } }
    # arr5: std::array<std::array<int, 3>, 2> = { {1, 2, 3} } # warning: suggest braces around initialization of subobject
    # arr6: std::array<std::array<int, 3>, 2> = {1, 2, 3}  # warning: suggest braces around initialization of subobject
    # arr7: std::array<std::array<int, 3>, 2> = {1}        # warning: suggest braces around initialization of subobject
    # arr8: std::array<std::array<int, 3>, 2> = 1        # error

    arr8: std::array<std::array<int, 3>, 2> = { { { {1} } } }

    std.cout << arr[3]
    std.cout << arr2[1]

    for (ll in [arr3, arr4]:
        std.cout << ll[0][0]
    )

    v = std.vector<int> (5, 42)
    std.cout << v[4]
    assert(v.size() == 5)

    # note these are parsed as 'BracedCall'
    v2 = std.vector<int> {5, 42}
    assert(v2.size() == 2)

    vv:std.vector<int> = std.vector<int> (5, 42)
    std.cout << v[4]
    assert(v.size() == 5)

    # 'BracedCall'
    vv2:std.vector<int> = std.vector<int> {5, 42}
    assert(v2.size() == 2)

    v1 : std.vector<int> = {1,2}
    vv1 : std.vector<std.vector<int>> = {v}
)
    