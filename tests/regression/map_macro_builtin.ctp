# Test Output 223

include <map>

def (main:
    # m: std.map = {"one"s:1, "two":2}  # error: all key-value pairs must be of the same type in map literal
    # m: std.map = {"one"s:1, "one"s:2}  # error: duplicate keys in map literal

    m: std.unordered_map = {"one"s: 1, s"two": 2}
    std.cout << m.at("two"s)

    mm: mut:std.map = {1: 2, 2: 3}
    std.cout << mm[1]

    mm2: std.map:mut = {1: 2, 2: 3}
    std.cout << mm2[2]
)
