from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from events import AuthEvent, EventKind

# The counting policy, isolated in one place. Only failed password guesses
# advance the threshold. The other parsed kinds stay available to the
# dashboard and to a future scan detector, but feeding them here would
# inflate totals ~3x and make the threshold meaningless.
COUNTED_KINDS = frozenset({EventKind.FAILED_PASSWORD})


@dataclass(frozen=True)
class Detection:
    """What the detector hands to the responder. Deliberately not an action --
    this module decides IF, Milestone 5 decides WHAT."""
    source_ip: str
    attempts: int
    window_start: datetime
    window_end: datetime


class BruteForceDetector:
    def __init__(self, threshold: int = 3, window_seconds: int = 600):
        if threshold < 1:
            raise ValueError("threshold must be at least 1")
        self.threshold = threshold
        self.window = timedelta(seconds=window_seconds)
        # ip -> deque of (timestamp, count). A deque because we push on the
        # right and pop from the left: O(1) both ends. list.pop(0) is O(n),
        # which over 290k events is the difference between fine and not.
        self._hits: dict[str, deque] = defaultdict(deque)
        self._flagged: set[str] = set()

    def observe(self, event: AuthEvent) -> Optional[Detection]:
        """Feed one event. Returns a Detection the first time an IP crosses
        the threshold, otherwise None."""
        if event.kind not in COUNTED_KINDS:
            return None

        q = self._hits[event.source_ip]
        # Store the multiplier rather than expanding it into N entries --
        # keeps rsyslog's collapsed repeats intact without inflating memory.
        q.append((event.timestamp, event.count))

        # Evict relative to THIS EVENT'S timestamp, not wall-clock now().
        # That single choice is what makes replaying a captured log produce
        # byte-identical results to watching it live, and it's why the tool
        # stays correct if it falls behind on a busy box.
        cutoff = event.timestamp - self.window
        while q and q[0][0] < cutoff:
            q.popleft()

        total = sum(count for _, count in q)
        if total < self.threshold:
            return None

        # Without this, a sustained attacker returns a Detection on every
        # subsequent event -- thousands of alerts for one attack. Milestone 6
        # replaces the flat set with cooldown + escalation.
        if event.source_ip in self._flagged:
            return None

        self._flagged.add(event.source_ip)
        return Detection(
            source_ip=event.source_ip,
            attempts=total,
            window_start=q[0][0],
            window_end=event.timestamp,
        )

    def prune(self, now: datetime) -> int:
        """Drop IPs with nothing left in the window. Call periodically.

        Without this, _hits grows for the lifetime of the process: one entry
        per IP ever seen. 1,914 IPs over 34 days is nothing, but this runs
        for months, and a defaultdict that only ever grows is a slow leak.
        """
        cutoff = now - self.window
        stale = [ip for ip, q in self._hits.items() if not q or q[-1][0] < cutoff]
        for ip in stale:
            del self._hits[ip]
        return len(stale)

    def tracked_ips(self) -> int:
        return len(self._hits)
