# SOP — Client Onboarding

| | |
|---|---|
| **Purpose** | Take a signed client from "contract returned" to "working normally" in five business days, with nothing important discovered late. |
| **Owner** | Virtual Assistant |
| **Approver** | Account lead (or the founder, in a solo practice) |
| **Frequency** | Per new client |
| **Time required** | ~2.5 hours of VA time, spread across 5 days |
| **Last reviewed** | 2026-09-01 |

---

## Why this exists

The expensive onboarding failures are all the same shape: a missing access
credential found in week three, an unstated invoicing preference, or an assumption
about who approves what. None are hard problems. They are only expensive because
they surface *after* work has started and the client has already formed a view.

This SOP front-loads the boring questions so week one is uneventful.

---

## Prerequisites

Do not start until **all** of these are true. Starting without them is the single
most common cause of a bad first month.

- [ ] Contract or engagement letter signed by both parties
- [ ] Scope, hours per week, and hourly rate agreed **in writing**
- [ ] A named primary contact, plus a named backup
- [ ] Payment method and invoicing schedule confirmed
- [ ] Start date agreed

> **Do not request any system access before the contract is signed.** If a client
> pushes for access first, that is a scope-and-payment risk, not an efficiency win.
> Escalate rather than accommodating it.

---

## Steps

### Day 1 — Kickoff and intake

1. **Send the welcome email.** Confirm start date, agreed hours, working timezone,
   the response-time expectation, and how to reach you. Keep it under 200 words.
2. **Send the intake form.** One form, not a conversation. It must capture:
   - Business overview and who the customers are
   - The three tasks they most want off their plate
   - Tools currently in use, with the account owner named for each
   - Communication preference (email / Slack / WhatsApp) and expected turnaround
   - Working hours, and which of those hours actually need overlap
   - Anything explicitly out of scope
3. **Book the kickoff call** for Day 2 or 3. 45 minutes. Send the agenda ahead.

### Day 2-3 — Kickoff call and access

4. **Run the kickoff call** against the agenda:
   - Walk through the intake answers and fill the gaps out loud
   - Agree what "done" looks like for each of the top three tasks
   - Agree the reporting rhythm (see `02-weekly-reporting.md`)
   - Confirm the approval path: what can be actioned alone, what needs a sign-off
5. **Request access.** One consolidated request, not a trickle. For each tool,
   record: tool name, access level needed, who grants it, date requested.
   - **Ask for delegated or role-based access, never a shared password.** Where a
     password manager is in use, request a shared vault entry.
   - For email, request *delegate access*, not the account password.
6. **Log every credential request** in the access tracker. An untracked request is
   the one that gets forgotten.

### Day 3-4 — Set up and document

7. **Confirm each access actually works** by logging in. "Access granted" and
   "access working" are different states, and the gap between them is usually a
   two-factor prompt going to someone else's phone.
8. **Build the client folder** to the standard structure:
   ```
   ClientName/
     01-admin/        contract, rates, invoices
     02-sops/         process docs specific to this client
     03-reporting/    weekly reports
     04-working/      live work
     05-archive/
   ```
9. **Draft the client-specific SOP** for the top task. Send it to the client for
   confirmation. This doubles as a check that you understood the task.
10. **Set up recurring calendar blocks** for the work and for the weekly report.

### Day 5 — First delivery and confirmation

11. **Complete one real task end to end** and deliver it. Something small and
    visible beats something large and unfinished.
12. **Send the week-one summary:** what was set up, what was delivered, what is
    still blocked and on whom, and what next week looks like.
13. **Confirm invoicing details** against the first invoice date.

---

## Edge cases

| Situation | What to do |
|---|---|
| Client will not grant access to a tool the scope requires | Document the blocker in writing, state what cannot be delivered without it, and proceed with everything else. Do not quietly absorb it. |
| Client offers a shared password to a personal account | Decline, and propose delegated access or a password-manager entry instead. If neither is possible, escalate — do not accept the credential. |
| Client asks for work outside the agreed scope in week one | Do it if it is under ~15 minutes and note it. If it is larger, respond with: "Happy to take that on — it sits outside our agreed scope, so shall I quote it separately or swap it against something else?" |
| Intake form comes back half-empty | Do not chase it twice by email. Bring the gaps to the kickoff call and fill them live. |
| Kickoff call is cancelled twice | Escalate. A client who will not spend 45 minutes at the start will not be reachable when something breaks. |
| Two-factor authentication is tied to the client's phone | Ask them to add you as a delegate, or to move that account to an authenticator app with a shared recovery path. Never route 2FA through a personal device without agreement. |

---

## Escalation path

1. **Blocked more than 24 hours** on access or a decision → email the primary
   contact, copy the backup contact.
2. **Blocked more than 72 hours** → escalate to the account lead. State the impact
   in hours and deliverables, not as a complaint.
3. **Anything touching money, contracts, or legal** → stop and escalate
   immediately. Never action a payment, a refund, or a contract change on a
   verbal instruction alone.
4. **Any request to move money, cash a cheque, or purchase gift cards** → stop,
   do not action, escalate immediately. This is the standard shape of a scam even
   when it appears to come from a known contact.

---

## Definition of done

Onboarding is complete when all of the following are true:

- [ ] All required access is granted **and verified by logging in**
- [ ] Client folder built to the standard structure
- [ ] At least one client-specific SOP written and confirmed by the client
- [ ] Recurring work and reporting blocks in the calendar
- [ ] One real deliverable shipped
- [ ] Week-one summary sent
- [ ] First invoice date confirmed

---

*Sample document. Written to a realistic composite scenario, not to a real
client's engagement. The structure and decisions are what I would use in practice.*
