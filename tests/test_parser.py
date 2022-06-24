from parser import parse, TupleLiteral, Module


def test_tuple():
    m = parse("""
(,)
    """)
    assert isinstance(m, Module)
    t, = m.args

    assert isinstance(t, TupleLiteral)
    assert t.args == []

