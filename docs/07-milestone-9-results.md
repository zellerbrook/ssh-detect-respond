# Milestone 9 — Threshold Justification: Results

_Run 2026-08-22 • Script: `threshold_sweep.py` • Data: `authlogs.tar.gz`_

**Status: numbers done and verified. Write-up not started.**

---

## START HERE NEXT SESSION

Milestone 9's analysis is complete. The only thing left is prose.

**Next action:** Claude drafts §3 of `05-grc-control-mapping.md` from the
findings below, with interviewer-defense notes attached. Zach then revises it
into his own voice — that revision pass is what makes it defensible, not just
authored.

**Why Milestone 9 was done out of order** (this got lost once already):
Milestones 5, 6, and 7 are all blocked behind building a dedicated
Debian/Ubuntu target VM, which does not exist yet. Milestone 9 needs no lab
at all. It was the only unblocked work.

**The five questions the write-up has to answer:**

1. What does this control do, and what kind of control is it?
2. Why 3 failures in 600 seconds and not 10 in 60?
3. What did the data show about false positives — and why is that number
   nearly useless on its own?
4. The operator's own IP got flagged. Was the detector wrong?
5. What does this control miss?

### Paste-ready prompt for the §3 writing session

```
I'm Zach — Navy musician transitioning to cybersecurity, targeting GRC.
Internship hunting starts soon. This is a WRITING session, not a build session.

THE BAR IS DESIGN LEVEL, NOT LINE LEVEL. GRC interviews ask what the control
does, why it's tuned that way, and what it misses. I need to defend every
design decision and its control implication.

PROJECT — SSH Detect + Respond (Python). Watches SSH auth logs, detects
brute-force patterns, auto-blocks the source IP. Framed for GRC as a detective
+ corrective control I built, mapped, and can defend. Full context is in the
project knowledge; read docs/07-milestone-9-results.md FIRST — it has the
findings and a "START HERE" block.

CURRENT STATE (as of 2026-08-22):
- Done: milestones 1 (parser), 2 (rotation-safe tail), 3 (sliding-window
  detector). All tested.
- Milestone 9 ANALYSIS IS DONE. threshold_sweep.py runs a 20-cell grid
  (threshold 2/3/5/10/20 x window 60/300/600/3600s) over 34 days of real
  auth.log. Numbers verified. Results in docs/07-milestone-9-results.md.
- Milestones 4-8 remain. 5, 6, 7 are blocked behind building a dedicated
  Debian/Ubuntu target VM that does not exist yet.

TONIGHT'S TASK: draft §3 of 05-grc-control-mapping.md — "the threshold as a
risk decision" — from the measured findings. You draft, with interviewer-
defense notes attached (the questions I'll be asked and the honest answers).
I then revise it into my own voice.

THE FOUR FINDINGS THAT MUST APPEAR:
1. Only ONE successful SSH login exists in 34 days, so the false-positive
   column has n=1. The "0.06%" figures are NOT rates and must not be
   published as rates. State the limitation.
2. The one false positive is ME — wrong username, 5 failures in ~115s from a
   T-Mobile carrier IP, correct key login next day. At 3/600 the control
   blocks me. This is simultaneously a false positive AND a correct
   detection: the detector sees behavior, not intent. Therefore the remedy is
   an allowlist (milestone 4), not a higher threshold.
3. Host scoping problem: the capture came from zachellerbrook-vps, which is
   now DECOMMISSIONED. Deployment target is the MacBook server 'zellerbrook',
   which has no comparable data. Say so plainly; frame re-derivation after 30
   days on the new host as continuous monitoring.
4. Coverage gap has a number: at 3/600, 397 of 1,878 failing IPs never
   crossed the threshold. Mean time-to-contain (within-burst) is 319s.

HONEST POSITIONING: this host is effectively key-only, so the control
delivers log hygiene and evidence generation, not credential-compromise
prevention. Volunteering that limitation is the assessor posture.

DATA HANDLING: authlogs.tar.gz is gitignored and must never be published —
1,914 real source IPs. Publish findings, withhold raw evidence. Do NOT
suggest synthesizing or regenerating the data; that would falsify the one
claim that gives this artifact value.

HONESTY: never be confidently wrong. NEVER assert a control ID, safeguard
number, or framework clause from memory — say you're unsure and have me
verify against the source document.

Start by reading docs/07-milestone-9-results.md, then draft §3.
```

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

2. **IP count.** Measured 1,914 distinct IPs (1,878 with failed passwords).
   `detector.py` comments claim 2,180. Reconcile or update the comment.

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

## Next actions

- [ ] Resolve host identity (blocks the scoping statement)
- [ ] Provide attested known-good IPs for the exception register
- [ ] Draft §3 of the write-up from these numbers
- [ ] Decide `authlogs.tar.gz` git vs `.gitignore` — it contains 1,914 real
      source IPs and one of your own carrier addresses
- [ ] Build the Debian/Ubuntu target VM (unblocks Milestones 5–7)
