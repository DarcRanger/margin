"""
tests/test_track_stats.py - Tests for GitHub traffic clones tracker.
"""

import json
import os
import tempfile
from unittest.mock import patch

from scripts.track_stats import (
    format_metric_count,
    load_history,
    merge_clone_records,
    run_tracker,
)


def test_format_metric_count():
    assert format_metric_count(0) == "0"
    assert format_metric_count(42) == "42"
    assert format_metric_count(307) == "307"
    assert format_metric_count(999) == "999"
    assert format_metric_count(1000) == "1K"
    assert format_metric_count(1200) == "1.2K"
    assert format_metric_count(12483) == "12.5K"
    assert format_metric_count(12400) == "12.4K"
    assert format_metric_count(100000) == "100K"
    assert format_metric_count(1000000) == "1M"
    assert format_metric_count(2500000) == "2.5M"


def test_merge_clone_records_authoritative_utc_dates():
    history = {
        "clones": {"total": 50, "unique": 30},
        "days": {
            "2026-09-01": {"clones": 20, "unique_cloners": 10},
            "2026-09-02": {"clones": 30, "unique_cloners": 20},
        },
    }

    # Incoming 14-day rolling window: updates Sept 2 and adds Sept 3, omitting Sept 1
    new_clones = [
        {"timestamp": "2026-09-02T00:00:00Z", "count": 35, "uniques": 22},
        {"timestamp": "2026-09-03T00:00:00Z", "count": 40, "uniques": 25},
    ]

    merge_clone_records(history, new_clones)

    # Invariant: Sept 1 outside rolling window is strictly retained
    assert "2026-09-01" in history["days"]
    assert history["days"]["2026-09-01"]["clones"] == 20

    # Sept 2 is updated to latest count
    assert history["days"]["2026-09-02"]["clones"] == 35
    assert history["days"]["2026-09-02"]["unique_cloners"] == 22

    # Sept 3 is appended
    assert history["days"]["2026-09-03"]["clones"] == 40
    assert history["days"]["2026-09-03"]["unique_cloners"] == 25

    # Totals recalculated across all dates: 20 + 35 + 40 = 95
    assert history["clones"]["total"] == 95
    assert history["clones"]["unique"] == 57


def test_merge_clone_records_empty_noop():
    history = {
        "clones": {"total": 10, "unique": 5},
        "days": {"2026-09-01": {"clones": 10, "unique_cloners": 5}},
    }
    merge_clone_records(history, None)
    assert history["clones"]["total"] == 10

    merge_clone_records(history, [])
    assert history["clones"]["total"] == 10


def test_load_history_schema():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "nonexistent.json")
        history = load_history(path)
        assert history["clones"]["total"] == 0
        assert history["days"] == {}


def test_run_tracker_end_to_end():
    with tempfile.TemporaryDirectory() as tmpdir:
        history_path = os.path.join(tmpdir, "history.json")

        mock_clones = [
            {"timestamp": "2026-09-14T00:00:00Z", "count": 42, "uniques": 31},
            {"timestamp": "2026-09-15T00:00:00Z", "count": 57, "uniques": 39},
        ]

        with patch("scripts.track_stats.fetch_clones", return_value=mock_clones):
            hist = run_tracker(
                repo="prxshetty/margin",
                traffic_token="mock_token",
                history_path=history_path,
            )

        assert hist["clones"]["total"] == 99
        assert hist["clones"]["unique"] == 70

        # Verify file on disk
        with open(history_path, "r", encoding="utf-8") as f:
            disk_hist = json.load(f)

        assert disk_hist["clones"]["total"] == 99
        assert disk_hist["clones"]["unique"] == 70
        assert "2026-09-14" in disk_hist["days"]
        assert "2026-09-15" in disk_hist["days"]
