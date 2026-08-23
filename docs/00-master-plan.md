# Cybersecurity Portfolio — Master Plan

_Owner: Zach • Created 2026-07-11 • Updated 2026-08-21 (GRC repivot) • Target: **GRC (primary)**; security-awareness trainer (downstream/secondary) • $100k+, Chicago • Separation: 2027-06-30_

---

## The idea in one line

Turn a stream of "learn it → build it → write it up → post it" into a portfolio that proves two things at once: that I can operate real systems, and that I can assess, document, and defend them as controls.

## The repivot (2026-08-21)

**Target changed from purple team to GRC.** What that does and doesn't change:

- **Doesn't change:** the flagship. SSH Detect + Respond is being finished, not scrapped. A GRC candidate who has built and assessed a real detective control beats one who has only written policy. GRC hiring screens out people who've never touched a system.
- **Does change:** the *framing*. Every project now answers control questions — what control is this, why is it configured this way, what evidence does it produce, what's the residual risk — alongside the technical ones. See `05-grc-control-mapping.md` for the flagship's version of that.
- **Does change:** the *depth bar*. See rule 1 below.
- **Does change:** the pipeline. Post-flagship projects shift from multi-week technical builds to weekend-scale assessment and documentation artifacts.

## How we use the Carter repo

The repo (`CarterPerez-dev/Cybersecurity-Projects`) is an **idea mine, not a syllabus.** We take the concepts, ignore the commercial upsell, and rebuild everything in our own way so the code is genuinely mine.

Three rules that make this hire-grade instead of resume-padding:

1. **Rebuild with understanding — at design level, not line level.** Read their version as a reference. Claude may narrate imports/classes/functions/design tradeoffs freely, and code can be drafted in Zed or via Claude Code. The bar is that I can defend **every design decision and its control implication** — not that I can recite syntax from memory. GRC interviews ask what the control does, why it's tuned that way, and what it misses; they don't ask me to whiteboard Python. This is a deliberate speed tradeoff made during the repivot, and it is the main reason the remaining timeline is workable. Keep the explain-it-back checkpoint after each piece.
2. **Make it ours.** Every project gets at least one deliberate change from the reference so it's honestly my work.
3. **Home-use test.** If I wouldn't run it on my own network — or wouldn't stand behind the assessment — it's the wrong project.

## Where TryHackMe fits

Optional, and only when a lab produces something postable. Lower priority after the repivot: THM rooms are attacker-perspective and don't feed GRC applications directly. Not removed — a clean "what this attack looks like from the defender's chair" piece still has value — but it doesn't compete with a finished assessment artifact for scarce hours.

## The write-up standard (this is the differentiator)

Every project ships with a write-up that works on **two levels in one document**:

- **Top layer — the non-technical read.** What problem this solves, why a normal person should care, the story. This is the security-awareness-trainer and future-consulting audience, and it's what makes the piece shareable. It also maps to a real GRC skill: explaining risk to people who don't work in security is most of the job.
- **Deep layer — the practitioner read.** Architecture, the security concepts, the decisions and trade-offs, how to run it, how it could be defeated. **Plus, since the repivot, a control section:** framework mappings, the risk decisions behind key parameters, evidence produced, residual risk.

A good test: your grandmother understands the first three paragraphs; a SOC lead respects the middle; an assessor respects the end.

## How this maps to the target role

| Target role | What it needs to see | How the plan delivers it |
|---|---|---|
| **GRC (primary)** | That I can map controls to frameworks, justify configuration as a risk decision, produce audit evidence, and communicate risk to non-technical stakeholders — and that I've actually touched systems, not just spreadsheets | Flagship is a real detective/corrective control I built, mapped to four frameworks, with a data-backed threshold justification. Post-flagship projects are assessment and documentation artifacts. Top layer of every write-up covers stakeholder communication. |
| **Security-awareness trainer (downstream/secondary)** | Evidence I can explain security to non-technical people | The top layer of every write-up + the parked personal-security training deliverable. Not a current target; do not let it pull scope. |

---

## Timeline (target: June 2027)

- **Internship hunting starts soon** — this is the near-term forcing function. The portfolio needs at least one finished, well-written-up project before applications go out.
- Skillbridge internship secured (Skillbridge itself starts March 2027)
- All personal projects live on the portfolio site
- Security+ studied and obtained — **more central after the repivot.** Security+ is the standard entry credential for GRC roles and shows up as a hard filter on job postings far more often than it did for the purple-team path. Worth scheduling deliberately, not fitting in around the edges.
- Separation: 2027-06-30

**Pacing note:** depth is the signal, but the calendar is real and it just got shorter. Momentum beats polish on any single milestone. One finished project with a control section beats three half-built tools.

## Sequence

1. **Flagship: SSH Detect + Respond.** Finish it, write it up with the GRC control section. → `01-flagship-ssh-detect-respond.md`, `05-grc-control-mapping.md`. Estimated 2–3 weeks from 2026-08-21.
2. **Take the site live** with the flagship already on it — no empty portfolio.
3. **Two weekend-scale GRC artifacts** from the pipeline below, to show breadth before applications.
4. **Draft the personal digital-security training outline and park it.**

> **Interrupt clause:** if the job asks for the security training on short notice, it jumps to the front. Everything else pauses cleanly.

## Candidate project pipeline (after the flagship)

Reworked for GRC. The old pipeline was five technical builds; most have been dropped or parked because they cost weeks and produce artifacts that speak to a purple-team audience. **Weekend-scale is the target.** Not committed — pick each when we get there.

| Project | What it produces | Est. |
|---|---|---|
| **CIS Controls v8 IG1 gap assessment of the homelab** | A real assessment report: scope, methodology, findings against IG1 safeguards, evidence, risk-rated remediation plan. Uses systems I actually run. | Weekend |
| **Risk register for the server + homelab** | Asset inventory, threat identification, likelihood/impact ratings, treatment decisions, residual risk statements. Pairs naturally with the gap assessment. | Weekend |
| **Third-party risk review of a SaaS I actually use** | Trust-center / SOC 2 report review, completed security questionnaire, recommendation memo. Third-party risk is a large share of entry-level GRC work and almost nobody has a sample. | Weekend |
| **Policy set written against the flagship** | 3–4 short policies (access control, logging & monitoring, incident response) where the SSH detector is the named implementing control. Demonstrates the full policy → control → evidence chain, which is the thing GRC actually does. | Weekend |
| **Simple Vulnerability Scanner** | The one technical build kept. CVE lookups against my own boxes; produces asset and vulnerability inventory — real artifacts for CIS 1/2/7 and RA-5. | ~1 week |

**Dropped or parked:** Canary Token Generator, Network Traffic Analyzer, Encrypted Password Manager — good projects, wrong audience for the time available. Phishing/Quishing analyzer stays parked with the awareness-training track.

Aim: the flagship plus 2–3 weekend artifacts before internship applications. Depth on the flagship, breadth on the rest.

## Definition of done (per project)

- [ ] Rebuilt with understanding at design level; I can defend the design choices and their control implications
- [ ] At least one deliberate change from the reference (technical projects)
- [ ] Runs on my own network / server, or assesses systems I actually operate
- [ ] Control mapping included, **verified against source framework documents** — never asserted from memory
- [ ] Key parameters justified as risk decisions, with data where data exists
- [ ] Residual risk stated
- [ ] Two-layer write-up published on the site, with the control section in the deep layer
- [ ] Repo is clean, licensed, and honest about what's mine
