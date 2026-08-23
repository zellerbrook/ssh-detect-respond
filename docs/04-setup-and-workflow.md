# Setup & Workflow — baseline for all projects

_Applies to every project in the portfolio, not just the flagship. Load this into the Build Lab project as knowledge._

> **Updated 2026-08-21 (GRC repivot).** Target role is now GRC. Forgejo dropped in favor of GitHub only. Coaching bar moved to design level. Paste-ready prompt at the bottom rewritten. See `00-master-plan.md` for strategy and `05-grc-control-mapping.md` for the control framing.

---

## The three roles of your kit

- **CachyOS desktop = where you write.** Zed is the daily driver; the working copy lives here. All authoring happens on the machine you fully control. (VS Code kept only for familiarity / team lingua franca.)
- **VirtualBox = where you test.** Attacker VM (Kali, later Parrot) and victim VMs (Metasploitable, vulnerable Win7/10) on an **isolated network** — host-only or internal — so an attack never leaks onto the real LAN. For a tool that runs *on* a host (like the SSH detector), the target is a dedicated **Debian/Ubuntu VM** that mirrors the server's OS.
- **MacBook Ubuntu server = where it runs for real.** Once a tool works in the VM lab, deploy here. An internet-facing SSH server also sees real brute-force traffic — real data for the write-up.

**Lifecycle per project:** write on CachyOS → test in the VM lab → deploy to the server. Git is the transport between all three (commit, push, pull to run) — no zip shuffling.

> **Status (2026-08-21):** VirtualBox and several guests exist, but the dedicated Debian/Ubuntu **target guest is not built yet**. Treat it as a prerequisite for the SSH detector's Milestone 5 (firewall response), not as current infrastructure. Match the guest's release to `zellerbrook` (check `/etc/os-release` and `systemctl is-active rsyslog` on the server first) — the server produces RFC3339 `auth.log` via rsyslog, and a journald-only guest would have no file to tail. Use a **host-only adapter** and give the guest a hostname distinct from `zellerbrook` so the two auth logs are never confusable side by side. Detection-only milestones (3 and 4) are safe to develop directly against `zellerbrook`; anything that writes firewall rules is not. `zellerbrook` is a MacBook with keyboard and screen attached, so a self-lockout is physically recoverable — annoying, not fatal.

## Git strategy — GitHub only

- **`origin` = GitHub. Forgejo is dropped** (decided 2026-08-21). Self-hosting a Gitea fork was never a prerequisite for building, it was costing momentum on server admin, and with internship applications approaching it doesn't earn its hours. GitHub is the current standard and it's where recruiters look.
- Keep repos honest: commit real WIP, don't curate history for appearances.

**Safety rule:** test firewall auto-blocking (or anything that can cut network access) **in the VM first, never first on a box you reach over SSH.** Self-lockout is the classic self-inflicted wound.

## Repo layout — one repo per project

Each portfolio project gets its own repo, not a monorepo. Rationale: a recruiter or hiring manager lands on one project and sees only that project. Repos live in `~/Projects/`.

```
ssh-detect-respond/
├── conftest.py             # empty; makes the root importable under bare `pytest`
├── requirements-dev.txt    # pytest, ruff — dev tooling, not runtime deps
├── events.py               # log line → AuthEvent (parser)
├── log_reader.py           # rotation-safe tail
├── detector.py             # sliding-window brute-force detection
├── authlogs.tar.gz         # 34 days of real auth.log from the server (~290k events, 2,180 IPs)
├── docs/                   # project knowledge; source of truth, re-uploaded to the Claude Project
│   ├── 00-master-plan.md
│   ├── 01-flagship-ssh-detect-respond.md
│   ├── 04-setup-and-workflow.md
│   ├── 05-grc-control-mapping.md        # GRC reframe: mappings, risk decisions, evidence
│   └── 06-project-instructions-draft.md # copy of the Claude Project custom instructions
└── tests/
    ├── test_events.py
    ├── test_log_reader.py
    ├── test_detector.py
    └── fixtures/
        └── sample_auth.log
```

**`authlogs.tar.gz` is a project asset, not clutter.** It's the dataset behind the threshold-justification analysis (flagship milestone 9). Check whether it belongs in git or in `.gitignore` with a note — 18MB of real auth logs from a live host may contain source IPs you'd rather not publish on GitHub. Worth a deliberate decision before the repo goes public.

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

## Coaching style (agreed session 7–8; bar revised 2026-08-21)

- **New syntax or library mechanics:** show the code first, then explain why it works. Socratic questioning on "what's this built-in called" wastes time and stalls momentum.
- **Design decisions, architecture, and debugging:** Zach reasons those out. That's where the defensibility actually comes from.
- **The bar is design level, not line level.** GRC interviews ask what the control does, why it's tuned that way, and what it misses — not for a Python whiteboard. Defend every design decision and its control implication; don't hold syntax in memory. Deliberate speed tradeoff made at the repivot.
- **Name the control angle as we build.** Which control is this, which framework, what evidence does it produce, what's the residual risk. Continuous, not a separate pass at the end.
- Keep the explain-it-back checkpoint after each piece either way.

---

## Paste-ready prompt for a fresh Build Lab chat

_Rewritten 2026-08-21 for the GRC repivot and the current milestone position. Update the CURRENT STATE block as milestones land — a stale state block is worse than none._

```
I'm Zach — Navy musician transitioning to cybersecurity, targeting GRC. Internship
hunting starts soon. This is a hands-on BUILD chat: you coach, I write the code.

THE BAR IS DESIGN LEVEL, NOT LINE LEVEL. GRC interviews ask what the control does, why
it's tuned that way, and what it misses — not for a Python whiteboard. I need to defend
every design decision and its control implication; I don't need to recite syntax. For
new syntax or library mechanics, show me the code first and then explain why; save the
questioning for design decisions and debugging.

PROJECT — SSH Detect + Respond (Python)
Watches SSH auth logs, detects a brute-force pattern, auto-blocks the attacking IP via
the firewall. Framed for GRC as a detective + corrective control I built, mapped, and
can defend. Full spec in this project's knowledge (01-flagship-ssh-detect-respond.md);
control framing in 05-grc-control-mapping.md.

CURRENT STATE (as of 2026-08-21):
- Done: milestone 1 parser (events.py), 2 rotation-safe tail (log_reader.py),
  3 sliding-window detector (detector.py). All tested.
- Next: milestone 4, allowlist / safeguards.
- Then: 5 firewall response w/ dry-run, 6 escalation + auto-expiry, 7 alerting,
  8 structured JSON output (locked as the deliberate upgrade), 9 threshold
  justification analysis against 34 days of my own auth logs.
- Estimated 2–3 weeks at a few evenings a week.

BLOCKER TO KNOW ABOUT: milestone 5 needs a dedicated Debian/Ubuntu target VM that
DOES NOT EXIST YET. Building it is a prerequisite. Milestone 9 needs no lab at all —
it's the one to grab if I have two spare hours.

GRC FRAMING — apply continuously, don't wait for me to ask:
- Name the control each piece implements and the framework it maps to.
- Treat parameters I choose as risk decisions needing justification, not tuning knobs.
- Surface the audit angle: what evidence this produces, what an assessor would ask,
  what the residual risk is.
- NEVER assert a control ID or framework clause from memory. Say you're unsure and
  have me verify against the source. A wrong control ID is what an interviewer catches.

MY SETUP / WORKFLOW:
- Write on my CachyOS desktop in Zed. Repos live in ~/Projects/.
- Test in VirtualBox on an ISOLATED network (host-only/internal): attacker = Kali VM,
  target = a dedicated Debian/Ubuntu VM. I only attack my own systems.
- Deploy to my MacBook Ubuntu server once it works in the VM.
- Git: GitHub as 'origin'. (Forgejo dropped.)

SAFETY — enforce this, flag before I act: anything that can cut network access
(firewall rules, blocks) gets tested in the VM FIRST, never first on a box I reach
over SSH.

HONESTY: never be confidently wrong. If you're unsure about syntax, a flag, an API, a
log format, a command, or a control reference — say so and have me verify.

Deliverable: working tool tested in the VM lab and deployed, a recorded demo clip, and
a two-layer write-up (non-technical intro + practitioner deep-dive with a control
section).

Start me at milestone 4. One thing at a time.
```
