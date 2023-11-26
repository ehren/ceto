from ceto.parser import parse
from ceto._abstractsyntaxtree import macro_matches

import pytest
import sys


pytest.skip(reason="-", allow_module_level=True)


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
    assert str(macro_matches(node1, pattern, parameters)) == "{'x': 1}"

    node2 = parse("2 + 3").args[0]
    assert str(matches(node2, pattern, parameters))  == "[{'x': 2}, {'x': 3}]"
    # print(str(macro_matches(node2, pattern, parameters)))  # None


def test_add_pattern_match():

    param = parse("y : IntegerLiteral").args[0]
    parameters = dict()
    parameters["y"] = param
    add_node = parse("0 + x + 1 + 2 + 3").args[0]
    add_pattern = parse("y + x + 1 + 2 + 3").args[0]
    assert str(matches(add_node, add_pattern, parameters)) == "{'y': 0}"


def test_binop_wildcard():

    param = parse("y : BinOp").args[0]
    parameters = dict()
    parameters["y"] = param
    add_node = parse("0 + (x + 1 + 2) + 3").args[0]
    add_pattern = parse("0 + y + 3").args[0]
    print( str(matches(add_node, add_pattern, parameters)))


def test_binop_wildcard2():

    param = parse("y : BinOp").args[0]
    parameters = dict()
    parameters["y"] = param
    add_node = parse("0 + x + 1 + 2 + 3").args[0]
    add_pattern = parse("y + 2 + 3").args[0]
    m = matches(add_node, add_pattern, parameters)
    assert str(m) == "{'y': ((0 + x) + 1)}"


def test_binop_wildcard3():

    param = parse("y : BinOp").args[0]
    parameters = dict()
    parameters["y"] = param
    add_node = parse("0 + x + 1 + 2 + 3").args[0]
    # add_pattern = parse("(0 + x) + 1 + y").args[0]
    add_pattern = parse("y + 3").args[0]
    print(str(matches(add_node, add_pattern, parameters)))

# test_constrained_wildcard_match()
# test_add_pattern_match()
test_binop_wildcard()
test_binop_wildcard2()
test_binop_wildcard3()
