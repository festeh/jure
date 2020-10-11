from bisect import bisect_left


class CellsIndex:
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

    def get_last_cell(self):
        if not self.index:
            return 0
        return self.index[-1]
