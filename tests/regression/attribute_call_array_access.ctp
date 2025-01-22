
def (main:
    v = [0, 1, 2]
    # std::cout << v.data()[2]  # TODO ensure test_parser is adequate (no longer allowed in codegen)
    std::cout << v.data().unsafe[2]
)
    
