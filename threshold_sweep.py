"""Threshold justification sweep — flagship Milestone 9.

Replays the 34-day auth.log capture through the real BruteForceDetector at a
grid of (threshold, window) settings and reports, for each cell, how many
source IPs would have been blocked and how many of those were legitimate.

This is NOT part of the shipped control. It is the *derivation* of the
control's configuration: the evidence behind "why 3 failures in 600 seconds"
rather than some other number. Commit it — when an assessor asks where the
threshold came from, this script and its output are the answer.

Usage:
    python threshold_sweep.py                    # reads ./authlogs.tar.gz
    python threshold_sweep.py --archive path.tar.gz
"""

import argparse
import gzip
import io
import tarfile
from collections import Counter, defaultdict

from detector import BruteForceDetector
from events import EventKind, parse_line

# Logrotate numbers files newest-to-oldest: auth.log is current, auth.log.4.gz
# is the oldest retained. We must feed them OLDEST FIRST.
#
# This is a correctness requirement, not tidiness. BruteForceDetector evicts
# with `cutoff = event.timestamp - self.window`. Feed events in reverse and
# every arriving event looks older than the cutoff, so each deque empties on
# every append and the totals never accumulate. The sweep would not crash --
# it would quietly report near-zero detections at every threshold and you'd
# publish a number that means nothing.
LOG_ORDER = [
    "var/log/auth.log.4.gz",
    "var/log/auth.log.3.gz",
    "var/log/auth.log.2.gz",
    "var/log/auth.log.1",
    "var/log/auth.log",
]

# The grid. Thresholds bracket the current default (3) in both directions;
# windows bracket the current default (600s) from one minute to one hour.
# Sweeping BOTH matters: window_seconds is just as much an undefended risk
# decision as threshold, and an interviewer who notices you justified one and
# not the other has found a real gap.
THRESHOLDS = (2, 3, 5, 10, 20)
WINDOWS = (60, 300, 600, 3600)


def iter_lines(archive_path):
    """Yield every log line from the archive, oldest file first.

    Reads straight out of the .tar.gz rather than extracting first. Two
    reasons: it keeps the run to a single command, and it avoids leaving
    ~73 MB of real auth logs -- containing live source IPs -- sitting
    unencrypted in the working tree of a repo headed for GitHub.
    """
    with tarfile.open(archive_path, "r:gz") as tar:
        for name in LOG_ORDER:
            member = tar.getmember(name)
            raw = tar.extractfile(member)
            # Members ending .gz are gzipped *inside* the tarball, so they
            # need a second decompression pass. The others are plain text.
            stream = gzip.GzipFile(fileobj=raw) if name.endswith(".gz") else raw
            # Logs are bytes; parse_line expects str. errors="replace" because
            # an attacker controls the username field and can put arbitrary
            # bytes in it -- one bad byte should not abort a 34-day run.
            for line in io.TextIOWrapper(stream, encoding="utf-8", errors="replace"):
                yield line


def run_sweep(archive_path):
    # One independent detector per grid cell. They all see the same event
    # stream in the same order; only their parameters differ. 20 detectors
    # over one pass of the data, rather than 20 passes.
    detectors = {
        (t, w): BruteForceDetector(threshold=t, window_seconds=w)
        for t in THRESHOLDS
        for w in WINDOWS
    }
    # Per cell: source_ip -> the Detection that fired for it.
    flagged = defaultdict(dict)

    # The legitimacy label (decision recorded in the write-up): an IP that
    # ever authenticated SUCCESSFULLY in these 34 days is treated as
    # legitimate. Blocking one is a false positive -- a real availability
    # impact on a real user. Cross-check this set against IPs you can
    # personally attest to before publishing; see the caveat in the output.
    accepted_ips = set()

    # For mean-time-to-contain: the first failed attempt we ever saw per IP.
    # Detection.window_start is the oldest attempt still INSIDE the window,
    # which is not the same thing once older attempts have been evicted.
    first_fail = {}

    kind_counts = Counter()
    failure_ips = set()
    all_ips = set()
    parsed = 0
    unparsed = 0
    out_of_order = 0
    prev_ts = None

    for line in iter_lines(archive_path):
        event = parse_line(line)
        if event is None:
            # Most of these are legitimately not auth events (cron, sudo,
            # systemd session lines). Reported as a coverage figure, not
            # silently dropped -- if this ratio looks wrong, the parser is
            # missing a log format and every number below is understated.
            unparsed += 1
            continue

        parsed += 1
        kind_counts[event.kind] += event.count
        all_ips.add(event.source_ip)

        if prev_ts is not None and event.timestamp < prev_ts:
            out_of_order += 1
        prev_ts = event.timestamp

        if event.kind is EventKind.ACCEPTED:
            accepted_ips.add(event.source_ip)
        elif event.kind is EventKind.FAILED_PASSWORD:
            failure_ips.add(event.source_ip)
            if event.source_ip not in first_fail:
                first_fail[event.source_ip] = event.timestamp

        for key, det in detectors.items():
            detection = det.observe(event)
            if detection is not None:
                flagged[key][event.source_ip] = detection

    return {
        "flagged": flagged,
        "accepted_ips": accepted_ips,
        "first_fail": first_fail,
        "kind_counts": kind_counts,
        "failure_ips": failure_ips,
        "all_ips": all_ips,
        "parsed": parsed,
        "unparsed": unparsed,
        "out_of_order": out_of_order,
    }


def report(r):
    print("=" * 78)
    print("DATASET")
    print("=" * 78)
    print(f"  lines parsed as sshd auth events : {r['parsed']:,}")
    print(f"  lines skipped (not sshd auth)    : {r['unparsed']:,}")
    print(f"  distinct source IPs              : {len(r['all_ips']):,}")
    print(f"  IPs with >=1 failed password     : {len(r['failure_ips']):,}")
    print(f"  IPs with >=1 ACCEPTED login      : {len(r['accepted_ips']):,}")
    print(f"  out-of-order events              : {r['out_of_order']:,}")
    print()
    print("  event totals by kind (rsyslog repeats expanded):")
    for kind, n in r["kind_counts"].most_common():
        print(f"    {kind.value:<22} {n:>10,}")
    print()

    print("=" * 78)
    print("THRESHOLD x WINDOW SWEEP")
    print("=" * 78)
    print("  Each cell: IPs blocked  (of which legitimate = false positives)")
    print()

    header = "  thresh |" + "".join(f"{w:>7}s " for w in WINDOWS)
    print(header)
    print("  " + "-" * (len(header) - 2))
    for t in THRESHOLDS:
        row = f"  {t:>6} |"
        for w in WINDOWS:
            hits = r["flagged"][(t, w)]
            fps = len(set(hits) & r["accepted_ips"])
            row += f"{len(hits):>5}({fps})".rjust(9)
        print(row)
    print()

    print("=" * 78)
    print("PER-CELL DETAIL")
    print("=" * 78)
    print(f"  {'setting':<14}{'blocked':>9}{'FPs':>6}{'FP rate':>9}"
          f"{'missed':>8}{'mean TTC':>11}{'median TTC':>12}")
    print("  " + "-" * 74)
    for t in THRESHOLDS:
        for w in WINDOWS:
            hits = r["flagged"][(t, w)]
            fp_ips = set(hits) & r["accepted_ips"]
            n = len(hits)
            fp_rate = (len(fp_ips) / n * 100) if n else 0.0
            # Coverage gap: IPs that produced failures but never crossed the
            # threshold. These are the attacks this setting does not see.
            missed = len(r["failure_ips"] - set(hits))
            ttcs = sorted(
                (d.window_end - r["first_fail"][ip]).total_seconds()
                for ip, d in hits.items()
                if ip in r["first_fail"]
            )
            if ttcs:
                mean_ttc = f"{sum(ttcs) / len(ttcs):,.0f}s"
                median_ttc = f"{ttcs[len(ttcs) // 2]:,.0f}s"
            else:
                mean_ttc = median_ttc = "-"
            label = f"{t}/{w}s"
            print(f"  {label:<14}{n:>9,}{len(fp_ips):>6}{fp_rate:>8.2f}%"
                  f"{missed:>8,}{mean_ttc:>11}{median_ttc:>12}")
    print()

    print("=" * 78)
    print("FALSE POSITIVES AT THE CURRENT DEFAULT (3 / 600s)")
    print("=" * 78)
    default = r["flagged"][(3, 600)]
    fp_ips = sorted(set(default) & r["accepted_ips"])
    if not fp_ips:
        print("  none — no IP that ever authenticated successfully was blocked")
    for ip in fp_ips:
        d = default[ip]
        print(f"  {ip:<18} {d.attempts:>4} attempts  "
              f"{d.window_start:%Y-%m-%d %H:%M:%S} -> {d.window_end:%H:%M:%S}")
    print()
    print("  CAVEAT: 'legitimate' here means the IP produced at least one")
    print("  ACCEPTED event in the capture. Cross-check against the IPs you")
    print("  can personally attest to before publishing, and confirm none of")
    print("  these successes were an attacker who eventually got in.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archive", default="authlogs.tar.gz")
    args = ap.parse_args()
    report(run_sweep(args.archive))


if __name__ == "__main__":
    main()
