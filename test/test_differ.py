from jure.utils import get_line_to_scroll


def test_differ_simple():
    old_lines = [s + '\n' for s in ['a', 'b', 'c', 'd', 'e']]
    new_lines = [s + '\n' for s in ['a', 'b', ' ', ' ', 'c', 'd', 'e']]
    diff_lines = get_line_to_scroll(old_lines, new_lines)
    assert diff_lines == 4
