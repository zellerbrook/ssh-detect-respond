# Scope

## What I planned

9 milestones. Log parsing, live tailing, brute-force detection, an allowlist, firewall response,
escalation and auto-expiry, alerting, structured JSON output, and a threshold justification.
Effectively a fail2ban I'd written myself.

## What I built

Milestones 1, 2 and 3: the parser, the rotation-safe tailer, and the sliding-window detector.
All tested, 20 tests.

Then milestone 9 out of order, because milestones 5 through 7 were all blocked behind building a
Debian target VM that didn't exist yet and milestone 9 needed no lab at all. It replays 34 days of
real auth logs through the detector at 20 different threshold and window settings, and reports
what each setting would have blocked. That analysis is in `docs/07-milestone-9-results.md`.

## What I cut

Milestones 4 through 8. The allowlist, the firewall response, escalation and auto-expiry,
alerting, and JSON output.

## Why I stopped

Two reasons. The second one is the useful one.

The first is that milestones 4 through 8 are the parts fail2ban and CrowdSec already do, and do
better. The problems I hadn't seen before were in the first three: what happens to a tailer when
a log rotates underneath it, and how you evict events from a sliding window in a way that survives
the process falling behind. By the end of milestone 3 I was past those. Everything after was
plumbing I'd have written worse than the tools that already exist.

The second is scoping, and it's why I'm writing this file instead of quietly not pushing anymore.

I built this in 30 to 60 minute sessions around a full-time job and 4 kids. Every milestone was
several sessions of work with nothing finished in between. So there was never a good place to
start and never a good place to stop, and the whole thing got put off, for weeks at a time. While
it sat at the top of my list it stopped everything behind it from moving too.

The rule I took out of it: the unit of work has to match the unit of output. If a session can't
end with something finished and committed, the scope is wrong, however good the idea is.

That's a scoping mistake, not a discipline one, and I'd rather write it down than let the repo
sit there implying I lost interest.

## What I'd tell someone starting this

Build the parser and the tailer. Write the rotation and truncation tests. Build the detector, and
make it evict against the event's own timestamp rather than the clock. Then take a real log
capture and sweep the threshold across it, because that's the part that turns a script into
something you can defend.

Then stop, and go read fail2ban's source with the understanding you just bought. That's about 20
hours of work and it's where the value is.

## What this does and doesn't demonstrate

It's a detective control. It reads authentication logs, recognises a brute-force pattern, and
reports it. It doesn't prevent anything and it doesn't respond, because those were the milestones
I cut.

The host the logs came from was effectively key-only in practice. Only 1 successful SSH login
appears in 34 days. So on that system this control delivers log hygiene and evidence, not
protection against credential compromise. Worth saying plainly rather than letting someone find
it in the numbers.

The threshold was derived from a host that has since been decommissioned. The machine this would
deploy to has a different exposure profile and no comparable capture. Control tuning is specific
to the environment it was tuned in, so that derivation would need doing again after 30 days of
data on the new host.

## Future work, if it ever comes back

The allowlist is the one worth building, and the data says why. At the current threshold this
control would have blocked me, from a mobile carrier address, after I fat-fingered a username 5
times in 2 minutes. Raising the threshold to fix that would hand every real attacker 7 more
guesses. So the fix is an exception list, and I now have a measured reason for that rather than
an assumption.

Everything else stays cut.
