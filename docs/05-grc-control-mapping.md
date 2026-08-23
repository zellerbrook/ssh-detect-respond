# Addendum — GRC Framing for SSH Detect + Respond

_Added 2026-08-21 • Supersedes nothing in `01-flagship-ssh-detect-respond.md`; adds a second audience to the same build._

---

## Why this addendum exists

The target role changed from purple team to GRC. The tool doesn't need to change. The **write-up** does.

A purple-team write-up answers: *how does this detect an attack?* A GRC write-up answers: *what control is this, why is it configured this way, and how would you prove to an assessor that it works?* Same code, different questions. The second set is what a GRC hiring manager is screening for, and it's the set most GRC candidates can't answer about anything they've actually touched.

The value proposition for an internship application becomes: **"I built a detective and responsive control, mapped it to four frameworks, justified the threshold as a risk decision, and produced the evidence an auditor would ask for."** That's a stronger story than a policy-writing exercise, because you can show the running system behind it.

---

## 1. What kind of control is this, actually

Before mapping anything, name the control precisely. Assessors care about this taxonomy and candidates routinely get it wrong.

| Dimension | This tool | Why |
|---|---|---|
| **Function** | Detective **and** corrective | Detects the brute-force pattern; then acts to contain it. Not preventive — it doesn't stop the first attempt. |
| **Implementation** | Technical / automated | No human in the loop between detection and response. |
| **Timing** | Near-real-time | Bounded by the 1-second tail poll in `log_reader.py`, not batch. |
| **Scope** | Host-level, single system | Not network-wide. This is a scoping limitation you should state, not hide. |

The honest positioning: **`fail2ban` is the production control; this is a from-scratch implementation built to understand the control's internals.** Say that in the write-up. GRC work constantly involves assessing tools you didn't build, and "I built one to understand how the assessment questions actually land" is a compelling reason to have done it.

---

## 2. Control mappings

> **Verify before publishing.** These IDs and titles are from memory and are directionally right, but exact control numbering and enhancement suffixes shift between framework revisions. Pull the actual text from the source (NIST SP 800-53 Rev 5 PDF, CIS Controls v8.1 workbook, CSF 2.0 Core, your ISO copy, AICPA TSC) and confirm each row before this goes on your site. A wrong control ID in a portfolio piece is worse than no control ID — it's the exact error an interviewer will catch.

### NIST SP 800-53 Rev 5

| Control | Title | How this tool relates |
|---|---|---|
| **AU-2** | Event Logging | Depends on it. `sshd` logging to `auth.log` is the control; this tool consumes its output. Note the dependency — a detective control is only as good as its log source. |
| **AU-6** | Audit Record Review, Analysis, and Reporting | Direct implementation. Automated, continuous review of auth records rather than periodic manual review. |
| **AU-6(1)** | — Automated Process Integration | The automation itself is the enhancement. |
| **AU-12** | Audit Record Generation | The tool's own event output (Milestone 8 JSON) generates a second-order audit record. |
| **AC-7** | Unsuccessful Logon Attempts | **Partial / compensating.** AC-7 as written is account-level lockout after N failures. This is *source-IP*-level. Different unit of enforcement — call that out rather than claiming clean coverage. It complements AC-7; it doesn't satisfy it. |
| **SI-4** | System Monitoring | Direct implementation for the SSH attack surface. |
| **SI-4(2)** | — Automated Tools for Real-Time Analysis | The sliding-window detector. |
| **SI-4(5)** | — System-Generated Alerts | Milestone 7. |
| **IR-4** | Incident Handling | Automated containment step of the handling process. |
| **IR-4(1)** | — Automated Incident Handling Processes | The block action. |
| **IR-5** | Incident Monitoring | Tracking of detections over time. |
| **SC-7** | Boundary Protection | The firewall rule insertion (Milestone 5). |
| **CM-3** | Configuration Change Control | **The interesting one.** Automated firewall changes are configuration changes made without human approval. See §4. |

### CIS Controls v8

| Safeguard | Title | Relevance |
|---|---|---|
| **4.4** | Implement and Manage a Firewall on Servers | The response mechanism. |
| **8.2** | Collect Audit Logs | Prerequisite. |
| **8.5** | Collect Detailed Audit Logs | The parser preserves username, invalid-user flag, and rsyslog repeat counts rather than flattening them. |
| **8.11** | Conduct Audit Log Reviews | Automated and continuous. |
| **13.1** | Centralize Security Event Alerting | Partial — single host. State the gap. |
| **17.4** | Establish and Maintain an Incident Response Process | The escalate → block → auto-expire sequence *is* a documented process. Write it up as one. |

Implementation-group note: these land in **IG1/IG2** territory. Worth stating which IG your homelab is scoped to and why — IG scoping is a real GRC skill and it's cheap to demonstrate.

### NIST CSF 2.0

| Subcategory | Coverage |
|---|---|
| **DE.CM-01** — Networks and network services are monitored | Direct |
| **DE.AE-02** — Potentially adverse events are analyzed | The detection window |
| **DE.AE-06** — Information on adverse events is provided to authorized staff | Alerting |
| **RS.MA-01** — The incident response plan is executed | Automated execution |
| **RS.MI-01** — Incidents are contained | The block |

### ISO/IEC 27001:2022 Annex A

| Control | Title |
|---|---|
| **A.8.15** | Logging |
| **A.8.16** | Monitoring activities |
| **A.8.20** | Networks security |
| **A.5.25** | Assessment and decision on information security events |
| **A.5.26** | Response to information security incidents |

### SOC 2 Trust Services Criteria

| Criterion | Relevance |
|---|---|
| **CC6.6** | Logical access boundary protection — the firewall response |
| **CC7.2** | Monitors system components for anomalies |
| **CC7.3** | Evaluates security events to determine whether they represent an incident |
| **CC7.4** | Responds to identified security incidents |

CC7.2 → CC7.3 → CC7.4 maps almost exactly onto detect → threshold → block. That's a clean narrative and worth calling out explicitly.

---

## 3. The threshold as a risk decision

This is the highest-value section of the whole addendum. Right now `detector.py` defaults to `threshold=3, window_seconds=600`. In a purple-team write-up that's a tuning parameter. In a GRC write-up it's a **risk acceptance decision that has to be justified and documented.**

Write it up in this structure:

**Risk being treated:** Unauthorized access via credential brute-forcing against an internet-exposed SSH service.

**Control objective:** Contain an automated password-guessing attack before it succeeds, without denying service to legitimate users.

**The tradeoff, stated numerically:**

- *Threshold too low* → false positives. A legitimate user fat-fingering a password three times in ten minutes gets their IP blocked. Availability impact, help-desk load.
- *Threshold too high* → the attacker gets more guesses before containment. Against a weak password, more guesses means real risk of compromise.

**Justification for 3/600:** Ground this in your own data. You have 34 days of real `auth.log` in `authlogs.tar.gz` — 290k events across 2,180 IPs, per the comments in `detector.py`. Run the detector across it at several thresholds and report the actual numbers:

| Threshold | IPs flagged | Legitimate IPs flagged (false positives) |
|---|---|---|
| 3 / 10 min | ? | ? |
| 5 / 10 min | ? | ? |
| 10 / 10 min | ? | ? |

**A threshold chosen from measured data on your own system, with the false-positive rate stated, is a genuine risk-based control decision.** Almost nobody at internship level can show that. This is maybe two hours of work using code you've already written, and it's the single strongest artifact in the project.

**Residual risk statement:** What this control does *not* cover — slow attacks under the threshold, distributed attacks from many IPs, credential stuffing with valid credentials on the first try, and the fact that a successful login from a never-before-seen IP isn't flagged at all. Name the residual risk and the compensating controls you'd recommend (key-only auth, MFA, network-level rate limiting). Naming what your control misses is what separates an assessor from a vendor.

---

## 4. Change control and the exception register

Two things the code already does that have direct GRC framing:

**The allowlist is an exception register.** Milestone 4's allowlist — loopback, your own IP, known-good networks — is exactly what an exception/whitelist register is in a compliance program: a documented, justified, reviewable set of carve-outs from a control. Write it up that way. Each entry gets a justification and, ideally, a review date. The safeguard test in the definition of done ("you tried to make it block your own IP and it refused") is a **control effectiveness test with a documented result** — that's audit evidence.

**Automated firewall changes are unapproved configuration changes.** Under CM-3, changing a firewall ruleset is a configuration change that normally requires approval. This tool makes them autonomously. That's not a flaw — it's a deliberate design decision that needs documenting:

- Why pre-approval is impractical (containment speed vs. approval latency)
- What the standing authorization would look like (a pre-approved change type with defined bounds)
- What bounds the automation (only single-IP blocks, only for SSH, auto-expiring after N hours, never touching allowlisted ranges)
- How changes are logged so the change record exists after the fact

**Dry-run mode is your change-testing control.** Milestone 5's dry-run isn't just a dev convenience — it's the pre-implementation validation step. Frame it as such.

**Auto-expiry is a reversibility control.** Milestone 6's auto-unblock bounds the blast radius of a false positive. That's a rollback mechanism, and rollback plans are a standard change-management requirement.

---

## 5. Evidence and metrics

An assessor asks: *show me this control is operating effectively.* Build the answer in.

**Evidence artifacts to produce:**

1. The tool's own event log (every detection, every block, every unblock, timestamped)
2. Structured JSON output — Milestone 8 — which is the machine-readable evidence feed and the SIEM-ingestion story
3. Firewall state before/after, captured in the demo
4. The safeguard test result (allowlist refusal)
5. Configuration file showing the approved threshold, version-controlled so changes are traceable

**Control effectiveness metrics** worth defining and reporting over your 34-day dataset:

- Detections per day
- Mean time from first failed attempt to block
- False-positive rate (blocks affecting legitimate sources)
- Coverage gap: attacks that stayed under threshold and were never flagged

Mean-time-to-contain is a metric that shows up in real security program reporting. Having a number for it, from your own system, is a talking point.

---

## 6. What changes in the build plan

**Nothing is removed. One thing is cut, one thing is added.**

- **Cut:** Milestone 8's dashboard and replay options. Take **structured JSON output** as the deliberate upgrade — smallest effort, and it's the one with a GRC story (machine-readable audit evidence, SIEM ingestion). Dashboard and replay move to "future work."
- **Add:** the threshold-justification analysis in §3. Runs on code you've already written against data you already have.

**Revised effort estimate.** Milestones 1–3 are done — `events.py`, `log_reader.py`, and `detector.py` exist with tests. That's the hardest third of the build, including the log-rotation handling and the regex-anchoring security fix. Remaining: allowlist (4), firewall response with dry-run (5), escalation and auto-expiry (6), alerting (7), JSON output (8), plus the threshold analysis. Realistically **2–3 weeks at a few evenings a week**, with the demo and write-up on top.

**Revised definition of done** — original list, plus:

- [ ] Control mapping table verified against source framework documents
- [ ] Threshold justified with measured false-positive data from the 34-day capture
- [ ] Residual risk statement written
- [ ] Allowlist documented as an exception register with justifications
- [ ] Automated-change-control rationale documented
- [ ] At least one control effectiveness metric reported with a real number

---

## 7. How the two-layer write-up changes

The two-layer structure still works; the deep layer gets a third section.

- **Top layer** — unchanged. What a brute-force attack is, why it matters, the demo clip.
- **Deep layer, part A (technical)** — unchanged. Log formats, tailing, sliding window, the regex-anchoring vulnerability you fixed, firewall automation, evasion.
- **Deep layer, part B (control)** — new. The control mappings, the threshold as a risk decision with data, the residual risk, the change-control and exception-register framing, the evidence artifacts and metrics.

For GRC applications, part B is the section you point to. For an internship application, consider pulling §3 out as a standalone short piece — "How I chose a detection threshold using thirty-four days of my own auth logs" is a better writing sample than a policy template, because it's yours and it has numbers in it.
