# Milestone 9 — Threshold Justification: Results

_Run 2026-08-22 • Script: `threshold_sweep.py` • Data: `authlogs.tar.gz` (not published; see
Data handling, below)_

This is the derivation of the detector's default threshold. It ran out of order, ahead of
milestones 4 through 8, because those needed a Debian target VM that didn't exist and this
needed no lab at all. It was the only unblocked work, and it turned out to be the part worth
doing. `SCOPE.md` covers why the rest was cut.

---

## What was run

`threshold_sweep.py` replays the full 34-day capture through the real
`BruteForceDetector` at 20 settings (threshold 2/3/5/10/20 × window
60/300/600/3600s) and reports, per cell, how many source IPs would have been
blocked and how many of those were legitimate.

The script is committed deliberately. It is not part of the shipped control —
it is the *derivation* of the control's configuration. When an assessor asks
where 3/600 came from, this script and its output are the answer. Add it to
the evidence list in §5 of `05-grc-control-mapping.md` as a sixth artifact.

## Dataset as measured

| Figure | Value |
|---|---|
| Date range | 2026-07-05 → 2026-08-08 (34 days) |
| Source host | `zachellerbrook-vps` |
| Raw log lines | 1,233,435 |
| Parsed as sshd auth events | 656,445 |
| Skipped (not sshd auth) | 576,990 |
| Distinct source IPs | 1,914 |
| IPs with ≥1 failed password | 1,878 |
| **IPs with ≥1 successful login** | **1** |
| Out-of-order events | 0 |

Event totals (rsyslog repeats expanded): failed_password 290,518 •
closed_preauth 208,874 • invalid_user 164,664 • accepted 1.

## The grid

Each cell: IPs blocked (of which legitimate).

| thresh | 60s | 300s | 600s | 3600s |
|---|---|---|---|---|
| 2 | 447 (1) | 1522 (1) | 1581 (1) | 1680 (1) |
| 3 | 328 (1) | 1121 (1) | **1481 (1)** | 1615 (1) |
| 5 | 283 (0) | 370 (1) | 1002 (1) | 1507 (1) |
| 10 | 220 (0) | 268 (0) | 309 (0) | 1339 (0) |
| 20 | 27 (0) | 226 (0) | 239 (0) | 1087 (0) |

Bold cell is the current default in `detector.py`.

---

## Finding 1 — the false-positive column has a sample size of one

The capture contains exactly **one** successful SSH login in 34 days. Every
"false positive rate" in the per-cell detail is one divided by a large number.
**These are not rates and must not be published as rates.** State the n=1
limitation explicitly; it is the first thing a reviewer would catch.

Root cause: the host is effectively key-only in practice. Password
authentication is not meaningfully in use by legitimate users.

## Finding 2 — the one false positive is Zach

```
08-07 01:46:59  Failed password for invalid user zach from 172.58.x.x
08-07 01:47:10  Failed password for invalid user zach from 172.58.x.x
08-07 01:48:07  Failed password for invalid user zach from 172.58.x.x
   (+2 more, second session, through 01:48:54)
08-08 00:46:40  Accepted publickey for root from 172.58.x.x  (ED25519)
```

Wrong username (`zach`; the account is `root`), five failures in ~115 seconds
from a T-Mobile carrier address, correct key-based login from the same IP the
next day.

**At the current default of 3/600, the control blocks this IP.**

This is more valuable than a clean false-positive rate would have been. It is
a documented self-lockout event from real production data, which converts
Milestone 4's allowlist from an asserted precaution into a control with
measured justification. It is also a ready-made control effectiveness test.

**The §3 argument, stated:** this is simultaneously a false positive *and* a
correct detection. Five failures from one source in two minutes is the
brute-force signature; the operator was behaviourally indistinguishable from
an attacker. The detector observes behaviour, not intent. Therefore the
remedy is an allowlist, not a higher threshold — raising the threshold to 10
would have spared this event but also grants every real attacker seven
additional guesses.

Settings that would NOT have blocked it: threshold 10 (all windows), and 5/60s.

## Finding 3 — `192.168.12.0/24` is the wrong allowlist for this host

Private LAN addresses can never appear as source IPs in a remote VPS's
`auth.log`; NAT rewrites them to the ISP-assigned public address. An allowlist
of `192.168.12.0/24` on the VPS would protect nothing while appearing to
protect everything — a worse failure than no allowlist, because it stops the
operator worrying about it.

The only confirmed-good source in the capture is a **mobile carrier IP**, and
carrier IPs rotate. Allowlisting by address is therefore weak here. Consider
whether the exception register should key on something more stable than
source IP.

## Finding 4 — mean-time-to-contain, corrected

The first version of the metric measured from the IP's first-ever failure,
which inflates results for scanners that probed weeks before being blocked
(mean 18,520s vs median 9s in one cell — a tell that the definition was wrong).

Measured **within the triggering burst** (`window_end - window_start`):

| Setting | Mean TTC | Median TTC |
|---|---|---|
| 3 / 600s | 319s | 358s |
| 5 / 600s | 365s | 460s |
| 10 / 600s | 146s | 60s |

Use 3/600 → **mean 319s** as the §5 control effectiveness metric. Note the
metric definition in the write-up; the ambiguity is real and an assessor may
ask which one you used.

## Finding 5 — coverage gap has a number now

At 3/600, 397 of the 1,878 IPs that produced failed passwords never crossed
the threshold. That is the residual risk in §3 with a measured figure behind
it, not a hand-wave.

---

## Verification performed

- Chronological ordering asserted: 0 out-of-order events across all five files.
- Monotonicity: detections fall as threshold rises and rise as window widens,
  with no violations in any of the 20 cells.
- Parse coverage cross-checked: grepped for `Accepted`, `session opened`, and
  `sshd.*session opened` across all five logs. Only one sshd success exists;
  the remaining 2,262 `session opened` lines are cron/sudo, not SSH. **The
  parser is not missing successful logins.**
- `failed_password` total of 290,518 matches the "~290k" figure in the
  `detector.py` comments.

## Discrepancies to resolve

1. **Host identity — RESOLVED 2026-08-22, with a consequence.**
   The capture is from `zachellerbrook-vps`, an old website server that has
   since been **decommissioned** (site moved to Cloudflare). It was never a
   part of this project beyond being the source of these logs. The deployment
   target is the MacBook Ubuntu server `zellerbrook`, which to date has only
   had logs pulled from it.

   Consequence for the write-up: **the threshold is derived from a host that
   no longer exists, and the deployment host has no comparable dataset.**
   State this plainly rather than letting a reviewer find it. Suggested
   framing — "threshold derived from 34 days of traffic on an
   internet-exposed host under my operation; the deployment target has a
   different exposure profile; re-derivation scheduled after 30 days of
   capture on the new host." Control tuning is environment-specific and
   requires periodic revalidation; volunteering that reads as maturity.

2. **IP count — RESOLVED.** Measured 1,914 distinct IPs (1,878 with failed
   passwords). An earlier `detector.py` comment claimed 2,180; the comment now
   reads 1,914 and matches the measurement.

3. ~~Root SSH login enabled on the VPS.~~ **Moot** — host decommissioned.
   Do not carry into the residual-risk section; it describes a system that
   no longer exists. Re-assess `zellerbrook`'s own SSH configuration instead.

## Data handling decision (2026-08-22)

`authlogs.tar.gz` contains 1,914 real source IPs, an operator carrier
address, attempted usernames, an ED25519 key fingerprint, and a hostname
containing the operator's real name. **It must not be published.**

Status: already listed in `.gitignore` since the initial commit; never
tracked; no blob present anywhere in git history. No remediation required.

Decision: **publish findings, withhold raw evidence.** The aggregate figures
in this document disclose nothing about any individual address and are what
the write-up actually needs.

Rejected: regenerating or simulating the traffic synthetically. The claim
that gives Milestone 9 its value is that the threshold was justified with
*measured* data from an operated system. Substituting invented data would
make that claim false, and fabricated evidence is an unrecoverable error for
a GRC candidate specifically.

Optional if reproducibility is wanted: pseudonymize source IPs via keyed
HMAC. `BruteForceDetector` groups by string equality and never parses
octets, so sweep output would be identical — verifiable by diffing against
`sweep_results.txt`. Not yet done.

## Positioning note (from the fail2ban comparison)

A fail2ban *jail* = log source + filter + ban policy. The equivalents here are
`log_reader.py`, the `MATCHERS` list in `events.py`, and `BruteForceDetector`
plus Milestones 5–6. Using that vocabulary in the write-up shows familiarity
with the reference architecture.

Because this host is effectively key-only, the honest claim is that the
control delivers **log hygiene and evidence generation, not
credential-compromise prevention** — on this system. Stating that limitation
unprompted is the assessor posture and is stronger than overselling.

The 576,990 skipped-line count is a usable canary: if it shifts sharply after
an OS upgrade, the filter has broken. Silent filter failure after a log-format
change is a known fail2ban failure mode and worth an explicit check.

---

## What this analysis does not settle

Two things stayed open when the project was scoped closed, and they are the
first work if it ever restarts.

The exception register has no attested known-good addresses in it. Finding 3
shows why that is harder than it looks here: the only confirmed-good source in
the capture is a mobile carrier IP, and carrier IPs rotate, so an
address-keyed allowlist is weak on this host specifically.

The threshold has not been re-derived on the deployment target. It comes from
a decommissioned VPS with a different exposure profile, and `zellerbrook` has
no comparable capture. Thirty days of data on the new host would be needed to
repeat this sweep there. Until that happens, 3/600 is a defensible number from
the wrong machine.
