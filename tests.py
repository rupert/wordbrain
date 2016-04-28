from wordbrain import Node, Grid, Point


def test_is_word():
    d = Node()
    d.add_word('foo')
    d.add_word('bar')

    assert d.is_word('foo')
    assert d.is_word('bar')

    assert not d.is_word('f')
    assert not d.is_word('fo')
    assert not d.is_word('hello')


def test_is_prefix():
    d = Node()
    d.add_word('foo')

    assert d.is_prefix('f', 3)
    assert d.is_prefix('fo', 3)
    assert d.is_prefix('foo', 3)

    assert not d.is_prefix('f', 0)
    assert not d.is_prefix('f', 1)
    assert not d.is_prefix('f', 2)
    assert not d.is_prefix('fooo', 3)
    assert not d.is_prefix('b', 3)


def test_solve():
    d = Node()
    d.add_word('PASS')
    d.add_word('FOO')
    d.add_word('BAR')

    grid = Grid([
        ['A', 'S'],
        ['S', 'P']
    ])
    solutions = grid.solve(d, [4])

    assert solutions == [
        [[Point(1, 1), Point(0, 0), Point(0, 1), Point(1, 0)]],
        [[Point(1, 1), Point(0, 0), Point(1, 0), Point(0, 1)]]
    ]

    for solution in solutions:
        assert grid.get_words(solution) == ['PASS']
