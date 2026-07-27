# Cybersecurity Portfolio — Master Plan

_Owner: Zach • Created 2026-07-11 • Updated 2026-07-27 (session 8) • Targets: purple team (primary) / security-awareness trainer (downstream/secondary), Chicago • Separation: 2027-06-30_

---

## The idea in one line

Turn a stream of "learn it → build it → write it up → post it" into a self-hosted portfolio of tools you actually run at home, each one defensible in an interview and each one teachable to a beginner.

## How we use the Carter repo

The repo (`CarterPerez-dev/Cybersecurity-Projects`) is an **idea mine, not a syllabus.** We take the concepts, ignore the commercial upsell, and rebuild everything in our own way so the code is genuinely yours.

Three rules that make this hire-grade instead of resume-padding:

1. **Rebuild with understanding.** Read their version as a reference. Claude may narrate imports/classes/functions/design tradeoffs freely — operator fluency is legitimate and valuable, not a shortcut — and code can be drafted in Zed or via Claude Code. No blank-file/from-memory rewrites; that's not the right drill for purple-team interviews (this isn't a SWE coding interview). Keep a quick "explain that back in plain language" checkpoint after each piece — cheap, and it's what stops this from becoming pure follow-along. Review still covers correctness, security, and whether you can defend the design choice. This is what survives interview questioning and what makes a real write-up possible.
2. **Make it ours.** Every project gets at least one deliberate change from the reference — a feature, a different design decision, a home-lab integration — so it's honestly your work, not a fork with the serial numbers filed off.
3. **Home-use test.** If you wouldn't run it on your own network, it's the wrong project. Tools you use are tools you remember and can talk about.

## Where TryHackMe fits

Optional, and only when a lab produces something postable. A TryHackMe room earns a place in the plan **if and only if** you can turn it into a quality write-up for the site (a walkthrough, a concept explainer, a "here's what this attack looks like from the defender's chair"). Labs you can't publish are practice, not portfolio — fine to do, but they don't go in this plan.

## The write-up standard (this is the differentiator)

Every project ships with a write-up that works on **two levels in one document**:

- **Top layer — the non-technical read.** What problem this solves, why a normal person should care, the story of the attack/defense. This is your security-awareness-trainer and future-consulting audience. It's also what makes the piece shareable.
- **Deep layer — the practitioner read.** Architecture, the security concepts, the decisions and trade-offs, how to run it, how it could be defeated. This is your purple-team hiring audience.

A good test: your grandmother understands the first three paragraphs; a SOC lead respects the rest. If a write-up only does one, it's not done.

## How this maps to your target roles

| Target role | What it needs to see | How the plan delivers it |
|---|---|---|
| **Purple team (primary)** | Evidence you understand attack *and* defense, and can automate response | Flagship is a full attack→detect→block loop you demo yourself. Later projects alternate offense/defense. |
| **Security-awareness trainer (downstream/secondary)** | Evidence you can explain security to non-technical people | The top layer of every write-up + the parked personal-security training deliverable. |

Purple team is the primary target — reprioritized in session 4 after realizing red-team work can be simpler and more lucrative than assumed. Security-awareness trainer is now downstream, likely to follow once you've built security experience, not a parallel primary target. The plan still feeds both from the same work.

---

## Timeline (target: June 2027)

- All personal projects live on the portfolio site
- Security+ studied and obtained
- Skillbridge internship secured (Skillbridge itself starts March 2027)
- Separation: 2027-06-30

Pacing note: depth is the signal, but the calendar is real. Momentum beats polish on any single milestone.

## Sequence (locked)

1. **Flagship: SSH Detect + Respond.** Build it, write it up. → see `01-flagship-ssh-detect-respond.md`
2. **Take the site live** with the flagship already on it — no empty portfolio. (Framework spec lives with the site project, built in a separate Claude Code session.)
3. **Draft the personal digital-security training outline and park it.** (Lives with the training project, not here.)
4. **Project #2 onward** — pick from the shortlist below, alternating offense/defense.

> **Interrupt clause:** if your job asks for the security training on short notice, it jumps to the front. The outline in step 3 exists so you can go from "asked" to "delivering" fast. Everything else pauses cleanly.

## Candidate project pipeline (after the flagship)

Mined from the repo, reshaped for your targets. Not committed — we pick each one when we get there.

- **Canary Token Generator** (deception / blue) — self-hosted honeytokens; superb teaching story ("digital tripwire"), fits your homelab.
- **Network Traffic Analyzer** (blue) — see what's actually on your wire; pairs with a "reading a packet capture for beginners" write-up.
- **Encrypted Password Manager** (crypto / privacy) — Argon2id + AES-GCM; leans into your privacy-first ethos, strong crypto explainer.
- **Simple Vulnerability Scanner** (offense-adjacent) — CVE lookups against installed software on your own boxes.
- **Phishing / Quishing analyzer** (awareness) — directly reusable inside the security-awareness training.

Aim: 3–4 strong, fully-written-up projects beat 10 half-built ones. Depth is the signal.

## Definition of done (per project)

- [ ] Rebuilt with understanding (not copy-pasted); you can explain every part and defend the design choices
- [ ] At least one deliberate change from the reference
- [ ] Runs on your own network / server
- [ ] Two-layer write-up published on the site
- [ ] Repo is clean, licensed, and honest about what's yours
