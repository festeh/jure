from enum import Enum


class EventType(Enum):
    RELOAD_PAGE = 1
    GO_TO_CELL = 2

reload_event = dict(type=EventType.RELOAD_PAGE)