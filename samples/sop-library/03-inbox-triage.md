# SOP — Inbox Triage

| | |
|---|---|
| **Purpose** | Process a client's inbox twice daily so that nothing needing action is missed, the client only sees what genuinely requires them, and no email is ever "handled" by being left unread. |
| **Owner** | Virtual Assistant |
| **Frequency** | Twice daily — 09:00 and 15:00 client time |
| **Time required** | 30-45 min per pass at ~80 emails/day, dropping to ~20 min once the filters mature |
| **Last reviewed** | 2026-09-01 |

---

## Why this exists

An inbox is not a to-do list, but it becomes one by default, and then it becomes
the client's anxiety. The job is not "reply to emails". The job is to make sure
that every message reaches exactly one of five fates, and that the client's own
attention is spent only on the small number that genuinely need a human decision
from them specifically.

The measure of success is not inbox zero. It is that **nothing actionable is ever
sitting unlabelled**, and that the client stops checking email out of worry.

---

## Prerequisites

- [ ] Delegate access to the mailbox (**not** the account password)
- [ ] Label taxonomy created and agreed with the client
- [ ] Filter rules built and tested against the last 30 days of mail
- [ ] Written agreement on what you may answer alone vs. what must go to the client
- [ ] A signature confirmed for messages sent on the client's behalf

---

## The taxonomy

Five labels. Resist adding a sixth — every extra label is a decision the triager
has to make, and ambiguity is what slows a pass down.

| Label | Meaning | Who acts |
|---|---|---|
| `1-Action-Client` | Needs the client specifically: a decision, an approval, a relationship reply | Client |
| `2-Action-VA` | Needs doing, and I can do it | VA |
| `3-Waiting` | Replied, awaiting someone else | VA follows up |
| `4-Reference` | No action, may be needed later | Nobody |
| `5-Archive` | No action, no future value | Nobody |

**The rule that makes it work:** an email in `1-Action-Client` must be there
because *only the client* can resolve it. If a competent assistant could handle it
with the agreed authority, it belongs in `2-Action-VA`. Every message wrongly put
in front of the client is a small withdrawal from the reason they hired a VA.

---

## Steps

### Each pass

1. **Sort oldest first.** Newest-first triage systematically strands the bottom of
   the inbox, and the bottom is where things go wrong.

2. **Handle in one pass. Touch each email once.** For each, choose exactly one:
   - **Under 2 minutes and within my authority** → do it now, then label `5-Archive`
   - **Needs me, longer than 2 minutes** → `2-Action-VA`, add to the task list with a due date
   - **Needs the client specifically** → `1-Action-Client` (see step 3)
   - **Awaiting a third party** → `3-Waiting`, set a follow-up date
   - **No action, might matter later** → `4-Reference`
   - **No action, no value** → `5-Archive`

3. **For anything going to the client, add the one-line summary.** Never forward a
   raw thread. Prepend:
   > **Needs from you:** [the decision, in one sentence]
   > **Context:** [one or two lines]
   > **My recommendation:** [what I would do]
   > **Deadline:** [date, or "none"]

   This is the highest-value habit in the whole SOP. It converts a five-minute read
   into a fifteen-second decision, and it is what a client is actually paying for.

4. **Draft replies for the client's approval** where the reply is routine but the
   voice must be theirs. Leave in Drafts, flag in the handover note.

5. **Work the `2-Action-VA` queue** against the task list, oldest and most urgent
   first.

6. **Sweep `3-Waiting`** for anything past its follow-up date. Chase once, politely,
   and reset the date. Two unanswered chases → move to `1-Action-Client`.

### End of day

7. **Send the handover note** — five lines maximum:
   - Emails processed today
   - Items now in `1-Action-Client`, with the most urgent named
   - Anything sent on their behalf
   - Anything still blocked and on whom
   - Drafts waiting for approval

8. **Confirm the inbox is fully labelled.** Zero unlabelled messages is the actual
   daily target — not zero messages.

### Weekly

9. **Review the filters.** Anything that reached the inbox and was archived without
   being read is a filter that should have caught it. Add the rule.
10. **Empty `4-Reference`** of anything older than 90 days that was never reopened.

---

## Edge cases

| Situation | What to do |
|---|---|
| An urgent email arrives between passes | Agree a definition of urgent at onboarding and set a filter that notifies you. Do not commit to continuous monitoring unless it is being paid for. |
| An angry client or customer email | Do not reply. `1-Action-Client` immediately, notify the client directly through the agreed channel. Tone-sensitive replies are never sent on someone's behalf without approval. |
| Something that looks like an invoice or a payment request | Never action it. `1-Action-Client` plus a direct message. Invoice fraud through a compromised or spoofed thread is common and specifically targets assistants with inbox access. |
| A request to change bank details on an existing supplier | Stop. Escalate immediately. Verify by phone on a number already on file — never a number in the email. This is the highest-loss failure mode in inbox work. |
| Sender is asking for something the client already declined | `5-Archive` if clearly settled, `1-Action-Client` if there is any doubt. When unsure, escalating is the cheaper error. |
| Personal mail in a business inbox | `4-Reference`, do not read further, and note the boundary at the next check-in. |
| Volume is far above the agreed level for a sustained period | Raise it at the weekly report with the actual numbers. Scope creep in inbox work is gradual and invisible until it is quoted in hours. |
| Genuinely unsure which label applies | `1-Action-Client` with a one-line note asking. Never leave it unlabelled — an unlabelled email is the only real failure state in this system. |

---

## Escalation path

1. **Anything about money, bank details, contracts, or legal** → do not action,
   escalate immediately, verify through a channel other than email.
2. **A suspected phishing or compromised account** → do not click anything, do not
   reply, notify the client directly by phone or chat, and flag it to whoever
   administers the mail domain.
3. **An email requiring a decision within 24 hours where the client is
   unreachable** → contact the named backup from onboarding.
4. **A recurring category with no clear owner** → raise at the weekly report and
   propose a rule, rather than re-deciding it every day.

---

## Definition of done, per pass

- [ ] Every message carries exactly one label
- [ ] Everything in `1-Action-Client` has its one-line summary and recommendation
- [ ] Follow-up dates set on everything in `3-Waiting`
- [ ] Handover note sent

---

## Week-one plan for a new inbox

Do not attempt full triage on day one. The taxonomy has to be earned.

| Day | Focus |
|---|---|
| 1 | Read only. Do not label. Learn who the recurring senders are and what normal looks like. |
| 2 | Agree the taxonomy and the authority boundary in writing. Build the labels. |
| 3 | Build filters against the last 30 days. Test, do not assume. |
| 4 | First supervised pass — label everything, send nothing without approval. |
| 5 | First independent pass. Handover note. Review with the client at the weekly report. |

---

*Sample document. Written to a realistic composite scenario (a solo consultant,
~80 emails/day, 15 meetings/week), not to a real client's mailbox.*
