# ssh-detect-respond

A small tool that reads SSH authentication logs and watches them for brute-force activity.

`fail2ban` already does this and does it better than I will. I built it to understand how it
works, and to find out what the questions look like from the inside.

## Status

Complete as scoped. Not under active development.

Milestones 1 through 3 are done: the parser, the rotation-safe tailer, and the sliding-window
detector, all tested. Milestone 9, the threshold justification, is done as analysis. Milestones
4 through 8 were cut on purpose. `SCOPE.md` says why.

## What it does

**Milestone 1, the parser.** Takes a line of text, decides whether it's an SSH login attempt,
and pulls four fields out of it: timestamp, source IP, username, and whether the attempt
succeeded. Everything else gets thrown away, which is most of the file.

```
Nov 12 09:15:22 target-vm sshd[2145]: Failed password for admin from 192.168.56.101 port 52344 ssh2
```

becomes

```python
AuthEvent(timestamp='Nov 12 09:15:22', source_ip='192.168.56.101',
          username='admin', outcome='Failed')
```

**Milestone 2, the tail.** Follows a growing log file the way `tail -f` does, starting at the
end so restarting the tool doesn't re-report last week's activity as if it were happening now.

It survives log rotation by checking whether the file sitting at that path is still the file it
opened, and reopening if it isn't. It handles the truncate-in-place case too.

Rotation is the part worth knowing about. Without that check the tool doesn't crash and doesn't
warn. It quietly stops seeing anything, forever, while looking completely fine. A security tool
that goes blind is worse than no tool at all, because you keep trusting it.

**Milestone 3, the detector.** Counts failed password attempts per source IP inside a sliding
time window and returns a detection the first time an IP crosses the threshold. Defaults are 3
failures in 600 seconds, and `docs/07-milestone-9-results.md` explains where those numbers came
from.

Two decisions in there are worth pointing at.

It evicts old events relative to the timestamp on the event being processed, not wall-clock
`now()`. That's what makes replaying a saved log produce the same result as watching one live,
and it's why the tool stays correct if it falls behind on a busy machine.

It counts only failed password attempts, though the parser recognises five kinds of sshd event.
Feeding all five into the threshold would roughly triple the totals and the threshold would stop
meaning anything. The other event types stay parsed and available for something else to use.

**Milestone 9, the threshold.** I replayed 34 days of real auth logs from a server I ran through
the detector at 20 different settings, and used the results to justify the default. 1,233,435 log
lines, 656,445 parsed events, 1,914 distinct source IPs. The numbers, the findings, and what they
don't support are in `docs/07-milestone-9-results.md`.

The short version: 3 failures in 600 seconds would have blocked 1,481 of the 1,878 IPs that ever
failed a password against that host, and it also would have blocked me. That event is written up
rather than hidden, because it's the argument for building an allowlist and it's the clearest
demonstration that the detector reads behaviour and has no access to intent.

## Running it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python log_reader.py
```

That follows `tests/fixtures/sample_auth.log`. Append a line to it from another terminal and it
shows up about a second later.

```bash
pytest
```

20 tests, covering parsing, rotation, truncation, the missing-file branch, and the detector's
window and threshold behaviour.

## Known limitations

These are real and unfixed:

- `parse_line` assumes every pattern matches. A line shaped differently than expected raises
  `AttributeError` instead of being skipped.
- The timestamp pattern misses single-digit days. Syslog pads them with two spaces (`Nov  2`)
  and the pattern expects one.
- The parser has never seen a log from a live internet-facing server in real time. The 34-day
  capture was replayed from disk, not tailed.
- Arch-based systems log to the systemd journal instead of `/var/log/auth.log`, so on my own
  machine this reads sample files rather than live ones.
- The detector holds state in memory only. Restarting it forgets every IP it was tracking, so an
  attacker who is patient across a restart starts from zero.
- The threshold was derived from a host that has since been decommissioned. The machine this
  would deploy to has a different exposure profile and no comparable dataset yet.

## Data handling

The 34-day capture is not in this repository and never has been. It contains 1,914 real source
addresses, attempted usernames, a key fingerprint, and one of my own carrier IPs. It's been in
`.gitignore` since the first commit and there's no blob for it anywhere in the history.

Findings get published. The evidence behind them stays local. Regenerating the traffic
synthetically would have been easy and would have made the one claim worth making false.

## Layout

```
events.py            event types and the sshd line matchers
log_reader.py        log follower, rotation and truncation handling
detector.py          sliding-window brute-force detector
threshold_sweep.py   replays a capture at 20 settings to derive the threshold
conftest.py          pytest path setup
tests/               parsing, rotation, truncation, missing file, detector
tests/fixtures/      sample auth log
docs/                project plan, control mapping, milestone 9 results
SCOPE.md             what I planned, what I built, why I stopped
```
