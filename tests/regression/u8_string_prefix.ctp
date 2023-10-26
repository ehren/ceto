# Test Output: 1

# u8string not recommended (string with prefix and suffix test)
def (main:
    u : std.u8string = u8"1"c
    s = std.string(u.begin(), u.end())
    std.cout << s
)
    