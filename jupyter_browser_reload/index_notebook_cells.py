from bisect import bisect_left


class CellIndex:
    def __init__(self, lines):
        cell_num = None
        self.index = []
        for line_num, line in enumerate(lines, 1):
            if line.startswith("# %%"):
                if cell_num is None:
                    cell_num = 0
                else:
                    self.index.append(line_num)

    def get_cell(self, line):
        return bisect_left(self.index, line)
