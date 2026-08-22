from datetime import datetime, timedelta, timezone

from detector import BruteForceDetector, Detection
from events import AuthEvent, EventKind

UTC = timezone.utc
T0 = datetime(2026, 8, 2, 3, 0, 0, tzinfo=UTC)


def fail(ip="1.2.3.4", offset_s=0, count=1):
    return AuthEvent(
        timestamp=T0 + timedelta(seconds=offset_s),
        kind=EventKind.FAILED_PASSWORD,
        source_ip=ip, username="root", invalid_user=False, count=count,
    )


def test_burst_trips_threshold():
    d = BruteForceDetector(threshold=3, window_seconds=600)
    assert d.observe(fail(offset_s=0)) is None
    assert d.observe(fail(offset_s=5)) is None
    hit = d.observe(fail(offset_s=10))
    assert isinstance(hit, Detection)
    assert hit.attempts == 3 and hit.source_ip == "1.2.3.4"


def test_slow_typos_do_not_trip():
    # you fat-fingering your password three times across an hour
    d = BruteForceDetector(threshold=3, window_seconds=600)
    for offset in (0, 900, 1800):
        assert d.observe(fail(offset_s=offset)) is None


def test_fires_once_per_ip_not_per_event():
    d = BruteForceDetector(threshold=3, window_seconds=600)
    hits = [d.observe(fail(offset_s=i)) for i in range(20)]
    assert sum(1 for h in hits if h is not None) == 1


def test_collapsed_repeat_counts_as_many():
    # one line carrying count=3 must trip a threshold of 3
    d = BruteForceDetector(threshold=3, window_seconds=600)
    assert d.observe(fail(count=3)) is not None


def test_ips_are_counted_independently():
    d = BruteForceDetector(threshold=3, window_seconds=600)
    for i in range(3):
        assert d.observe(fail(ip="1.1.1.1", offset_s=i)) is None or i == 2
    assert d.observe(fail(ip="2.2.2.2", offset_s=0)) is None


def test_non_counted_kinds_are_ignored():
    d = BruteForceDetector(threshold=1, window_seconds=600)
    e = AuthEvent(timestamp=T0, kind=EventKind.INVALID_USER,
                  source_ip="1.2.3.4", username="admin", invalid_user=True)
    assert d.observe(e) is None


def test_prune_drops_stale_ips():
    d = BruteForceDetector(threshold=3, window_seconds=600)
    d.observe(fail(offset_s=0))
    assert d.tracked_ips() == 1
    assert d.prune(T0 + timedelta(hours=2)) == 1
    assert d.tracked_ips() == 0
