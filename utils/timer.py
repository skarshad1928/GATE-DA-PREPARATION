from __future__ import annotations

import time


def start_timer() -> float:
    return time.perf_counter()


def elapsed_seconds(started_at: float | None) -> int:
    if started_at is None:
        return 0
    return max(0, round(time.perf_counter() - started_at))
