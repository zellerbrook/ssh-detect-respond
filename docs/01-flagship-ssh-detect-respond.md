# Flagship — SSH Detect + Respond

_Language: Python • Home: your MacBook Ubuntu server • Story: a full purple-team loop in one project_

---

## Why this is the flagship

It does something most beginner projects don't: it shows **both sides**. You play the attacker (run a brute-force against your own SSH), and your tool plays the defender (detects the pattern, blocks the IP, alerts you). One project, one demo, and a hiring manager sees you understand offense, defense, and automated response. It also runs on a box you already own — so it's real, not a toy.

## Our scope (how ours differs from the reference)

The repo's version is a log parser → detector → firewall blocker. We keep that spine and make it ours with **one deliberate upgrade to pick from** (choose when we build):

- A small **live status dashboard** (terminal or tiny local web page) showing current watched IPs, strikes, and blocks — great for the demo and screenshots.
- A **"replay" mode** that reads a captured attack log and narrates what the detector sees, step by step — doubles as a teaching aid for the write-up.
- **Structured JSON event output** so the tool could feed a SIEM later — signals you're thinking like a purple-teamer, not just scripting.

Pick one for v1; the others become "future work" in the write-up.

## Build milestones (rebuild-with-understanding)

Each milestone is a checkpoint where you should be able to explain what you wrote before moving on.

1. **Log reader.** Parse `/var/log/auth.log` (Ubuntu) lines into structured events: timestamp, source IP, username, result. Understand the exact log formats for failed password, invalid user, and accepted login.
2. **Tail without re-reading.** Follow the file as it grows, survive log rotation, and track position so you never double-count. (This is the part people get wrong — worth doing carefully.)
3. **Detection window.** Count failures per IP inside a sliding time window (e.g. 5 in 10 min = attack). Make the threshold configurable. Distinguish a fat-fingered password from an actual attack.
4. **Allowlist / safeguards.** Never block your own IP, the loopback, or your known-good networks. This safeguard comes *before* any blocking code — self-lockout is the classic self-inflicted wound.
5. **Response.** Add the offending IP to the firewall (UFW or iptables) programmatically. Start with a dry-run mode that logs what it *would* do before it does it for real.
6. **Escalation + auto-unblock.** Alert first, then rate-limit, then block; auto-expire blocks after N hours; manual unblock command.
7. **Alerting.** At minimum a local log + one channel you actually use. Keep it simple for v1.
8. **Your chosen upgrade** (dashboard / replay / JSON) from the scope section.

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
- `fail2ban` already does much of this in production — say so. Your value isn't reinventing it, it's **understanding it from the inside** and being able to build/modify detection logic. That framing is honest and it's exactly what purple team wants.

## Write-up plan (two layers, one document)

- **Top layer:** "What a brute-force attack actually is, and how a tripwire that fights back works." The story, the stakes, the demo clip. Understandable by anyone.
- **Deep layer:** log formats and why tailing is tricky, the sliding-window detection design, the self-lockout safeguard, firewall automation, escalation/unblock, how an attacker could evade it (slow/distributed attempts) and what you'd do about it, and how `fail2ban` compares.
- **Optional TryHackMe tie-in:** if there's an SSH/brute-force room that gives you a clean attacker's-eye view worth publishing, fold a short "from the attacker's chair" section in. Only if it's genuinely postable.

## Definition of done

- [ ] Every milestone rebuilt from scratch and explainable
    - [x] 1. Log reader (`parse_line`)
    - [x] 2. Tail without re-reading (`try_read_line` / `follow_log`)
    - [ ] 3. Detection window
    - [ ] 4. Allowlist / safeguards
    - [ ] 5. Response
    - [ ] 6. Escalation + auto-unblock
    - [ ] 7. Alerting
    - [ ] 8. Chosen upgrade
- [ ] Tests covering the non-obvious paths (log rotation, truncation, missing file)
- [ ] Your one deliberate upgrade is in
- [ ] Safeguard proven (you tried to make it block your own IP and it refused)
- [ ] Demo recorded on an isolated target
- [ ] Two-layer write-up drafted
- [ ] Clean repo: README, license, honest "what's mine vs. inspired by" note

## When we build

Say the word and we start at the next open milestone — I'll coach it, you write it. Bring the repo's version open in a tab as reference; we read it, then close it and build ours.
