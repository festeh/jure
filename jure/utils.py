import difflib
import os
from pathlib import Path
from typing import List

from loguru import logger


def get_lines_file(file_path):
    with open(file_path) as f:
        return f.readlines()


def get_diffing_lines(old_lines, new_lines) -> List[int]:
    diffs = difflib.Differ().compare(old_lines, new_lines)
    lin_num = 0
    diffing_lines_num = []
    diffing_lines = []
    for line in diffs:
        code = line[:2]
        if code in ("  ", "+ "):
            lin_num += 1
        if code == "+ ":
            diffing_lines.append(line)
            diffing_lines_num.append(lin_num)
    logger.info(f"Diff. lines numbers: {diffing_lines_num}")
    logger.info(f"Diff. lines: {diffing_lines}")
    return diffing_lines_num


def get_file_path_from_notebook_path(notebook_path):
    notebook_path = Path(notebook_path)
    return notebook_path.parent / f"{notebook_path.stem}.py"


def get_notebook_path_from_file_path(file_path):
    file_path = Path(file_path)
    return file_path.parent / f"{file_path.stem}.ipynb"


def get_file_update_timestamp(file_path):
    statbuf = os.stat(file_path)
    timestamp = statbuf.st_mtime
    return timestamp
