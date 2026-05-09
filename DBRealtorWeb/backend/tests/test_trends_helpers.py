"""Unit tests for pure helpers in src.routers.trends (no DB required)."""

from src.routers.trends import NewPerDayPoint, _drop_initial_load_spike


def _pts(*counts: int) -> list[NewPerDayPoint]:
    return [
        NewPerDayPoint(date=f"2026-04-{i + 1:02d}", count=c)
        for i, c in enumerate(counts)
    ]


def test_drops_obvious_initial_seed_spike() -> None:
    points = _pts(3149, 120, 80, 95, 110, 70, 130)
    out = _drop_initial_load_spike(points)
    assert [p.count for p in out] == [120, 80, 95, 110, 70, 130]


def test_keeps_first_when_not_an_outlier() -> None:
    points = _pts(150, 120, 80, 95, 110, 70, 130)
    out = _drop_initial_load_spike(points)
    assert len(out) == len(points)
    assert out[0].count == 150


def test_short_series_is_returned_unchanged() -> None:
    # Below the minimum length needed for a stable median.
    points = _pts(3149, 100)
    out = _drop_initial_load_spike(points)
    assert len(out) == 2


def test_zero_median_does_not_drop() -> None:
    # If the rest is all zeros there is no meaningful baseline to compare against.
    points = _pts(50, 0, 0, 0, 0)
    out = _drop_initial_load_spike(points)
    assert len(out) == len(points)


def test_empty_series_is_safe() -> None:
    assert _drop_initial_load_spike([]) == []
