from enum import Enum


class EventType(Enum):
    RELOAD_PAGE = 1
    GO_TO_CELL = 2


reload_event = dict(type=EventType.RELOAD_PAGE)


def scroll_event(cell_num):
    return {"type": EventType.GO_TO_CELL, "value": cell_num}
