from enum import Enum


class JobStatus(Enum):
    QUEUED = 1
    ACTIVE = 2
    PAUSED = 3
    CANCELED = 4
    DONE = 5