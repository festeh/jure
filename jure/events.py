from enum import Enum


class EventType(Enum):
    RELOAD_PAGE = 1
    HANDLE_CHANGED_CELLS = 2


reload_event = dict(type=EventType.RELOAD_PAGE)


def cells_changed_event(diffing_cells, cell_to_scroll):
    return {"type": EventType.HANDLE_CHANGED_CELLS,
            "changed_cells": diffing_cells,
            "cell_to_scroll": cell_to_scroll}
