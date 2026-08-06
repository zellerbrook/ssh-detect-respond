# ssh-detect-respond

A small tool that reads SSH authentication logs and watches them for brute-force activity.

`fail2ban` already does this and does it better than I will. I'm building it to understand how it works, and someday to compare mine against it.

## Status

Milestones 1 and 2 are done. The tool parses auth log lines and follows a live log file. It doesn't decide anything is an attack yet. That's milestone 3.

## What it does

**Milestone 1, the parser.** Takes a line of text, decides whether it's an SSH login attempt, and pulls four fields out of it: timestamp, source IP, username, and whether the attempt succeeded. Everything else gets thrown away, which is most of the file.

```
Nov 12 09:15:22 target-vm sshd[2145]: Failed password for admin from 192.168.56.101 port 52344 ssh2
```

becomes

```python
AuthEvent(timestamp='Nov 12 09:15:22', source_ip='192.168.56.101',
          username='admin', outcome='Failed')
```

**Milestone 2, the tail.** Follows a growing log file the way `tail -f` does, starting at the end so restarting the tool doesn't re-report last week's activity as if it were happening now.

It survives log rotation by checking whether the file sitting at that path is still the file it opened, and reopening if it isn't. It handles the truncate-in-place case too.

Rotation is the part worth knowing about. Without that check the tool doesn't crash and doesn't warn. It quietly stops seeing anything, forever, while looking completely fine. A security tool that goes blind is worse than no tool at all, because you keep trusting it.

## Running it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python log_reader.py
```

That follows `tests/fixtures/sample_auth.log`. Append a line to it from another terminal and it shows up about a second later.

```bash
pytest
```

## Known limitations

These are real and unfixed:

- `parse_line` assumes every pattern matches. A line shaped differently than expected raises `AttributeError` instead of being skipped.
- The timestamp pattern misses single-digit days. Syslog pads them with two spaces (`Nov  2`) and the pattern expects one.
- The parser has never seen a log from a real internet-facing server. Everything so far is a saved sample.
- Arch-based systems log to the systemd journal instead of `/var/log/auth.log`, so on my own machine this reads sample files rather than live ones.

## Layout

```
log_reader.py             parser and log follower
conftest.py               pytest path setup
tests/test_log_reader.py  parsing, rotation, truncation, missing file
tests/fixtures/           sample auth log
docs/                     project plan and setup notes
```
