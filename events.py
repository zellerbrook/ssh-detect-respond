import re
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

RFC3339_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
SYSLOG_RE = re.compile(r"^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})")


class EventKind(str, Enum):
    """What kind of auth event a line represents.

    Subclassing str (not just Enum) means these serialize straight to JSON
    without a custom encoder -- relevant if you pick the SIEM-output upgrade
    at Milestone 8.
    """
    FAILED_PASSWORD = "failed_password"
    ACCEPTED = "accepted"
    INVALID_USER = "invalid_user"
    CLOSED_PREAUTH = "closed_preauth"
    MAX_AUTH_EXCEEDED = "max_auth_exceeded"


@dataclass
class AuthEvent:
    timestamp: datetime          # always timezone-aware UTC
    kind: EventKind
    source_ip: str
    username: Optional[str]
    invalid_user: bool = False   # was the account nonexistent?
    count: int = 1               # >1 when rsyslog collapsed repeats


IP = r"([0-9]{1,3}(?:\.[0-9]{1,3}){3})"

# rsyslog collapses identical consecutive lines into a summary. The original
# message survives inside the brackets, so we unwrap it and carry N forward
# as a multiplier rather than losing 10,950 attempts.
REPEATED_RE = re.compile(r"message repeated (\d+) times: \[ (.+)\]\s*$")

# Order matters: first match wins. Every pattern captures the same three
# groups -- (invalid-flag, username, ip) -- so one handler serves them all.
MATCHERS = [
    (EventKind.FAILED_PASSWORD,
     re.compile(r"Failed password for (invalid user )?(\S+) from " + IP + r" port")),
    (EventKind.ACCEPTED,
     re.compile(r"Accepted \S+ for (invalid user )?(\S+) from " + IP + r" port")),
    (EventKind.MAX_AUTH_EXCEEDED,
     re.compile(r"maximum authentication attempts exceeded for (invalid user )?(\S+) from " + IP + r" port")),
    (EventKind.INVALID_USER,
     re.compile(r"(Invalid )user (\S+) from " + IP + r" port")),
    (EventKind.CLOSED_PREAUTH,
     re.compile(r"Connection (?:closed|reset) by (invalid |authenticating )user (\S+) " + IP + r" port")),
]


def _parse_syslog_ts(raw, now):
    """Traditional syslog: no year, no timezone -- both inferred."""
    ts = datetime.strptime(f"{now.year} {raw}", "%Y %b %d %H:%M:%S").astimezone()
    if ts - now > timedelta(days=1):
        ts = datetime.strptime(f"{now.year - 1} {raw}", "%Y %b %d %H:%M:%S").astimezone()
    return ts.astimezone(timezone.utc)


def parse_timestamp(line, now=None):
    """Always returns timezone-aware UTC, or None. Never naive."""
    if now is None:
        now = datetime.now(timezone.utc)
    first = line.split(" ", 1)[0]
    if RFC3339_RE.match(first):
        if first.endswith("Z"):          # fromisoformat rejects 'Z' before 3.11
            first = first[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(first).astimezone(timezone.utc)
        except ValueError:
            return None
    m = SYSLOG_RE.match(line)
    return _parse_syslog_ts(m.group(1), now) if m else None


def parse_line(line, now=None):
    """Turn one log line into an AuthEvent, or None if it isn't one."""
    # Unwrap a collapsed repeat first, so the inner message goes through the
    # normal matchers and we keep the multiplier.
    rep = REPEATED_RE.search(line)
    multiplier, body = (int(rep.group(1)), rep.group(2)) if rep else (1, line)

    for kind, pattern in MATCHERS:
        m = pattern.search(body)
        if not m:
            continue
        ts = parse_timestamp(line, now=now)   # timestamp comes from the OUTER line
        if ts is None:
            return None
        flag, username, ip = m.group(1), m.group(2), m.group(3)
        return AuthEvent(
            timestamp=ts,
            kind=kind,
            source_ip=ip,
            username=username,
            # "invalid user bob" means bob doesn't exist. Keep that as a flag
            # instead of baking it into the username string like the old
            # parser did -- 'invalid user admin' was never a real username.
            invalid_user=bool(flag and flag.strip().lower().startswith("invalid")),
            count=multiplier,
        )
    return None
