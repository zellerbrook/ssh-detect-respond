# Flagship — SSH Detect + Respond

_Language: Python • Home: your MacBook Ubuntu server • Story: a detective + corrective control you built, assessed, and can defend_

> **GRC reframe (2026-08-21).** The target role changed to GRC mid-build. This project is being **finished, not scrapped** — the code doesn't change, the write-up gains a control section. Read `05-grc-control-mapping.md` alongside this file; it holds the framework mappings, the threshold-as-risk-decision analysis, and the evidence/metrics plan. Estimated 2–3 weeks remaining as of 2026-08-21.

---

## Why this is the flagship

For a GRC candidate, it answers the question that screens most people out: *have you actually touched a system?* This is a real detective and corrective control — it detects a brute-force pattern in live auth logs and contains it by writing a firewall rule — running on a box you own, seeing real internet traffic. You can map it to NIST 800-53, CIS v8, CSF 2.0, ISO 27001, and SOC 2; justify its threshold with thirty-four days of your own data; and state what it misses. Almost nobody at internship level can do that about anything they built.

The attacker-side demo still earns its place: it's how you prove the control works, and it makes the write-up watchable.

**Honest positioning, state it plainly:** `fail2ban` is the production control. This is a from-scratch implementation built to understand the control's internals. That's a strength — GRC work is mostly assessing tools you didn't build, and having built one is why the assessment questions land.

## Our scope (how ours differs from the reference)

The repo's version is a log parser → detector → firewall blocker. We keep that spine and make it ours with one deliberate upgrade.

**Locked (2026-08-21): structured JSON event output.** Smallest remaining effort, and the only option with a GRC story — machine-readable audit evidence and a SIEM-ingestion path. `EventKind` already subclasses `str` specifically so it serializes without a custom encoder.

**Moved to "future work" in the write-up:** the live status dashboard and the attack-replay teaching mode. Both are good; neither is worth the weeks right now.

## Build milestones (rebuild-with-understanding)

Each milestone is a checkpoint where you should be able to explain **the design decision and its control implication** before moving on — design level, not line level (see master plan, rule 1).

1. **Log reader.** Parse `/var/log/auth.log` (Ubuntu) lines into structured events: timestamp, source IP, username, result. Understand the exact log formats for failed password, invalid user, and accepted login.
2. **Tail without re-reading.** Follow the file as it grows, survive log rotation, and track position so you never double-count. (This is the part people get wrong — worth doing carefully.)
3. **Detection window.** Count failures per IP inside a sliding time window. Make the threshold configurable. Distinguish a fat-fingered password from an actual attack. *Control angle: the threshold is a risk decision, not a tuning knob — see §3 of the GRC addendum.*
4. **Allowlist / safeguards.** Never block your own IP, the loopback, or your known-good networks. This safeguard comes *before* any blocking code — self-lockout is the classic self-inflicted wound. *Control angle: this is an exception register. Each entry gets a justification.*
5. **Response.** Add the offending IP to the firewall (UFW or iptables) programmatically. Start with a dry-run mode that logs what it *would* do before it does it for real. *Control angle: dry-run is pre-implementation change validation; autonomous firewall edits need a documented change-control rationale.*
6. **Escalation + auto-unblock.** Alert first, then rate-limit, then block; auto-expire blocks after N hours; manual unblock command. *Control angle: auto-expiry is the rollback mechanism that bounds a false positive.*
7. **Alerting.** At minimum a local log + one channel you actually use. Keep it simple for v1.
8. **Structured JSON event output** (locked — see scope above). *Control angle: machine-readable audit evidence.*
9. **Threshold justification analysis.** *New with the GRC reframe.* Sweep the threshold across the 34-day capture in `authlogs.tar.gz`, count detections and false positives at each setting, and report the numbers. Uses code already written; roughly two hours. **This is the single strongest artifact in the project** — a control threshold justified with measured data from your own system.

## The demo (this is what you show and screenshot)

On an isolated setup (a VM or a second machine on your LAN, **never** a production box you rely on):

1. Show the tool running, watching clean.
2. From another machine, run a controlled SSH brute-force against your test box (e.g. `hydra` against a throwaway account, or a simple scripted loop).
3. Watch the tool detect the burst, cross the threshold, and drop the IP into the firewall.
4. Show the attacker now blocked, the alert fired, and the event logged.
5. Show auto-unblock (or manual unblock) restoring access.

Record it. That 60–90 second clip is portfolio gold and goes at the top of the write-up.

## Safety + ethics (state these in the write-up, and mean them)

- Attack only your **own** systems, on a network you control. Never point the brute-force at anything you don't own.
- Use a disposable target account; don't test against your real logins.
- `fail2ban` already does much of this in production — say so. Your value isn't reinventing it, it's **understanding it from the inside**. For a GRC audience that framing is stronger, not weaker: assessing controls you didn't build is the job, and having built one is why you can ask the right questions about it.

## Write-up plan (two layers, one document)

- **Top layer:** "What a brute-force attack actually is, and how a tripwire that fights back works." The story, the stakes, the demo clip. Understandable by anyone. *This layer is also the GRC stakeholder-communication sample — explaining risk to non-security people is most of the job.*
- **Deep layer, part A — technical:** log formats and why tailing is tricky, the sliding-window detection design, the regex-anchoring vulnerability found and fixed (a crafted username could forge a source IP), the self-lockout safeguard, firewall automation, escalation/unblock, and how an attacker could evade it.
- **Deep layer, part B — control:** *new with the reframe.* Framework mappings, the threshold as a data-backed risk decision, residual risk, the exception register and change-control rationale, evidence artifacts and effectiveness metrics. Full detail in `05-grc-control-mapping.md`. **For GRC applications, this is the section you point to.**
- **Consider pulling §3 out as a standalone piece.** "How I chose a detection threshold using thirty-four days of my own auth logs" is a better writing sample than a policy template — it's yours and it has numbers in it.
- **TryHackMe tie-in:** deprioritized after the repivot. Only if it's genuinely postable and costs nothing.

## Definition of done

- [ ] Every milestone built and defensible at design level
    - [x] 1. Log reader (`parse_line`)
    - [x] 2. Tail without re-reading (`try_read_line` / `follow_log`)
    - [x] 3. Detection window (`BruteForceDetector`) — written and tested; confirm the explain-back checkpoint is done
    - [ ] 4. Allowlist / safeguards
    - [ ] 5. Response
    - [ ] 6. Escalation + auto-unblock
    - [ ] 7. Alerting
    - [ ] 8. Structured JSON output
    - [~] 9. Threshold justification analysis — **numbers done 2026-08-22**
          (`threshold_sweep.py`, results in `07-milestone-9-results.md`);
          §3 write-up still to draft
- [ ] Tests covering the non-obvious paths (log rotation, truncation, missing file)
- [ ] Safeguard proven (you tried to make it block your own IP and it refused) — *this is a control effectiveness test; record the result as evidence*
- [ ] Demo recorded on an isolated target
- [ ] Two-layer write-up drafted, including the control section

**GRC additions** (from `05-grc-control-mapping.md`):

- [ ] Control mapping table verified against source framework documents
- [ ] Threshold justified with measured false-positive data from the 34-day capture
- [ ] Residual risk statement written
- [ ] Allowlist documented as an exception register with justifications
- [ ] Automated-change-control rationale documented
- [ ] At least one control effectiveness metric reported with a real number

- [ ] Clean repo: README, license, honest "what's mine vs. inspired by" note

## When we build

Next open milestone is **4 — allowlist / safeguards**. Say the word and we start there; I'll coach it, you write it.

Two scheduling notes: milestone 5 needs the dedicated Debian/Ubuntu target VM, which **does not exist yet** (see `04-setup-and-workflow.md`) — building it is a prerequisite, not a side quest. And milestone 9 is independent of everything else, so it's the one to grab if you have two spare hours and no lab access.
