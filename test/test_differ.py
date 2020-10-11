from jure.utils import get_diffing_lines


def test_differ_simple():
    old_lines = [s + '\n' for s in ['a', 'b', 'c', 'd', 'e']]
    new_lines = [s + '\n' for s in ['a', 'b', ' ', ' ', 'c', 'd', 'e']]
    diff_lines = get_diffing_lines(old_lines, new_lines)
    assert diff_lines == [3, 4]
