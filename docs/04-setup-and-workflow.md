# Setup & Workflow — baseline for all projects

_Applies to every project in the portfolio, not just the flagship. Load this into the Build Lab project as knowledge._

---

## The three roles of your kit

- **CachyOS desktop = where you write.** Zed is the daily driver; the working copy lives here. All authoring happens on the machine you fully control. (VS Code kept only for familiarity / team lingua franca.)
- **VirtualBox = where you test.** Attacker VM (Kali, later Parrot) and victim VMs (Metasploitable, vulnerable Win7/10) on an **isolated network** — host-only or internal — so an attack never leaks onto the real LAN. For a tool that runs *on* a host (like the SSH detector), the target is a dedicated **Debian/Ubuntu VM** that mirrors the server's OS.
- **MacBook Ubuntu server = where it runs for real.** Once a tool works in the VM lab, deploy here. An internet-facing SSH server also sees real brute-force traffic — real data for the write-up.

**Lifecycle per project:** write on CachyOS → test in the VM lab → deploy to the server. Git is the transport between all three (commit, push, pull to run) — no zip shuffling.

> **Status (2026-08-21):** VirtualBox and several guests exist, but the dedicated Debian/Ubuntu **target guest is not built yet**. Treat it as a prerequisite for the SSH detector's Milestone 5 (firewall response), not as current infrastructure. Match the guest's release to `zellerbrook` (check `/etc/os-release` and `systemctl is-active rsyslog` on the server first) — the server produces RFC3339 `auth.log` via rsyslog, and a journald-only guest would have no file to tail. Use a **host-only adapter** and give the guest a hostname distinct from `zellerbrook` so the two auth logs are never confusable side by side. Detection-only milestones (3 and 4) are safe to develop directly against `zellerbrook`; anything that writes firewall rules is not. `zellerbrook` is a MacBook with keyboard and screen attached, so a self-lockout is physically recoverable — annoying, not fatal.

## Git strategy — local first, Forgejo deferred, GitHub for reach

- **`origin` = GitHub.** Forgejo on the MacBook server is the eventual plan (self-hosted Gitea fork, private source of truth for messy WIP), but standing it up is deferred — it is not a prerequisite for building, and blocking project work on server admin was costing momentum. Revisit once the flagship is deployed.
- **GitHub for reach.** Recruiters look at GitHub, so public visibility there serves the hiring goal directly. Until Forgejo exists, keep repos honest: commit real WIP, don't curate history for appearances.

**Safety rule:** test firewall auto-blocking (or anything that can cut network access) **in the VM first, never first on a box you reach over SSH.** Self-lockout is the classic self-inflicted wound.

## Repo layout — one repo per project

Each portfolio project gets its own repo, not a monorepo. Rationale: a recruiter or hiring manager lands on one project and sees only that project. Repos live in `~/Projects/`.

```
ssh-detect-respond/
├── conftest.py             # empty; makes the root importable under bare `pytest`
├── requirements-dev.txt    # pytest, ruff — dev tooling, not runtime deps
├── log_reader.py
├── docs/                   # project knowledge; source of truth, re-uploaded to the Claude Project
│   ├── 00-master-plan.md
│   ├── 01-flagship-ssh-detect-respond.md
│   └── 04-setup-and-workflow.md
└── tests/
    ├── test_log_reader.py
    └── fixtures/
        └── sample_auth.log
```

`README.md` is absent by design for now — it gets written when the project is ready for the GitHub mirror, since it's a portfolio artifact rather than a build artifact. It's tracked on the flagship's definition-of-done list.

**Docs are versioned with the code.** The `docs/` folder is the source of truth. The copies attached to the Claude Project are downstream — re-upload them when the knowledge needs refreshing.

## Testing conventions

- Run with `python -m pytest` or bare `pytest`; the empty root `conftest.py` makes both work by putting the project root on `sys.path`.
- Tests live in `tests/`, fixtures in `tests/fixtures/`.
- Prioritize the paths that are hard to reason about and easy to get wrong — log rotation, truncation, races — over the obvious happy path. Those are the ones worth defending in an interview.

## Baseline toolchain to verify at the start of each build

- **Dev box (CachyOS):** `python3`, `venv`, `pip`, `git`, `ruff` (lint/format), `pytest`, Zed.
- **Git:** `origin` (GitHub) set on the repo. Forgejo remote added later.
- **VM lab:** attacker + target on an isolated VirtualBox network; project-specific tools (e.g. `hydra` on the attacker, `ufw`/`iptables` on the target).

## Editor guidance by project size

- **Short, single-file tools:** Vim is fine.
- **Multi-file packages (most projects, incl. the flagship):** Zed — you get a language server, integrated git, and a debugger without leaving your ethos.

## Coaching style (agreed session 7–8)

- **New syntax or library mechanics:** show the code first, then explain why it works. Socratic questioning on "what's this built-in called" wastes time and stalls momentum.
- **Design decisions, architecture, and debugging:** Zach reasons those out. That's where the interview-defensibility actually comes from.
- Keep the explain-it-back checkpoint after each piece either way.

---

## Paste-ready prompt for the Build Lab's first chat

```
I'm Zach — Navy musician transitioning to cybersecurity (targeting purple team /
security-awareness trainer). This is a hands-on BUILD chat: you coach, I write the
code. I rebuild with understanding. If I can't explain a line, we don't ship it.
For new syntax or library mechanics, show me the code first and then explain why;
save the questioning for design decisions and debugging.

FIRST PROJECT — SSH Detect + Respond (Python)
Watches SSH auth logs, detects a brute-force pattern, auto-blocks the attacking IP via
the firewall. A full purple-team loop: I play attacker, my tool plays defender. Full
spec is in this project's knowledge (01-flagship-ssh-detect-respond.md).

REFERENCE (idea mine, not a syllabus — ignore the upsell, we build our own):
github.com/CarterPerez-dev/Cybersecurity-Projects  → SSH Brute Force Detector

MY SETUP / WORKFLOW (baseline for all my projects):
- Write on my CachyOS desktop in the Zed editor. Repos live in ~/Projects/.
- Test in VirtualBox on an ISOLATED network (host-only/internal): attacker = Kali VM,
  target running the detector = a dedicated Debian/Ubuntu VM. I only attack my own
  systems.
- Deploy to my MacBook Ubuntu server for real use once it works in the VM.
- Git: GitHub as 'origin'. Self-hosted Forgejo is planned but deferred.
- Editor note: Zed is my daily driver; I keep VS Code only for familiarity.

BEFORE MILESTONE 1 — establish my software baseline (do this first, one thing at a
time, tell me exactly what to run and what to install if missing):
- Dev box (CachyOS): python3, venv, pip, git, ruff, pytest, Zed.
- Git: confirm the GitHub 'origin' remote is set.
- VM lab: Kali attacker + Debian/Ubuntu target on an isolated VirtualBox network;
  hydra on the attacker for the controlled brute-force; ufw/iptables on the target.

THEN build in milestones — I must explain each before moving on:
1. Log reader (parse /var/log/auth.log into structured events)
2. Tail without re-reading (survive log rotation, track position)
3. Detection window (N failures per IP in T minutes; configurable)
4. Allowlist / safeguards (NEVER block my own IP — build this BEFORE any blocking)
5. Response (add IP to firewall; start in dry-run mode)
6. Escalation + auto-unblock
7. Alerting (local log + one channel I use)
8. My one deliberate upgrade so it's honestly mine: live status dashboard, OR
   attack-replay teaching mode, OR JSON event output for a future SIEM (I'll pick).

Deliverable: working tool tested in the VM lab and deployed to my server, a recorded
demo clip, and a two-layer write-up (non-technical intro + practitioner deep-dive).

Coach me starting with the software baseline. Ask me one thing at a time.
```
