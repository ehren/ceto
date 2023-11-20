from ceto.parser import parse
from ceto._abstractsyntaxtree import macro_matches

def matches(node, pattern, parameters):
    m = macro_matches(node, pattern, parameters)
    if m:
        return m
    submatches = []
    for a in node.args:
        m = macro_matches(a, pattern, parameters)
        if m:
            # return m
            submatches.append(m)
    if node.func:
        m = macro_matches(node.func, pattern, parameters)
        if m:
            submatches.append(m)
    return submatches


def test_constrained_wildcard_match():

    pattern = parse("x").args[0]
    param = parse("x : IntegerLiteral").args[0]
    node1 = parse("1").args[0]
    parameters = dict()
    parameters["x"] = param
    assert str(macro_matches(node1, pattern, parameters)) == "{x: 1}"

    node2 = parse("2 + 3").args[0]
    print(str(matches(node2, pattern, parameters)))# == "{x: 2}"  # returns first match only. might have to rethink
    print(str(macro_matches(node2, pattern, parameters)))# == "{x: 2}"  # returns first match only. might have to rethink



test_constrained_wildcard_match()