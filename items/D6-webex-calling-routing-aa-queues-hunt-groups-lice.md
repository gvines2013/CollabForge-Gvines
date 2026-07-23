# D6 · Webex Calling Routing: AA, Queues, Hunt Groups & Licensing

> **Blueprint domain:** Domain 3 — Call Control & Dial Plan  ·  **Item type coverage:** scenario Q&A

**After this item you can:**

- Parse requirement language into the right routing construct, with the feature matrix to prove it
- Design queue behavior end to end: distribution, overflow, callback, supervision
- Validate every design against the license-type feature matrix

## Concepts & theory

_Read each topic in three passes — the **concept**, the **worked example**, the **exam angle** — then close the page and re-derive the design rule from memory._

### Topic 1 · The four constructs — and the keyword map

Webex Calling gives four ways to route a call to people. Auto Attendant: an IVR menu with schedules ('press 1 for sales'). Call Queue: callers WAIT — hold music, position announcements, staffed distribution. Hunt Group: immediate distribution to members by a policy, no waiting room. Shared Line Group: the same number appears as a line on multiple devices. Requirement language maps almost mechanically onto these.

- 'menu', 'options', 'business hours greeting' → Auto Attendant.
- 'wait', 'position', 'callback', 'supervisor', 'reports' → Call Queue.
- 'ring the team', 'longest idle', 'no announcements' → Hunt Group.
- 'same number on several phones', 'boss/admin share' → Shared Line Group.

**Worked example.** Parse: 'Callers to the service desk choose hardware or software, wait with announcements, and team leads need weekly answer-time reports.' Three keywords → AA (choose) fronting two Call Queues (wait + announcements) with analytics (reports). A hunt group fails twice: no queuing, no reports. Write the dismissal explicitly — Design answers score on stated reasoning.

**Exam angle.** Most items are exactly this parse. Practice mapping each clause to a construct AND naming why the runner-up loses.

### Topic 2 · Auto Attendant design: menus, schedules, the front door

An AA owns a number/extension, plays greetings, and routes key presses to destinations (users, queues, hunt groups, voicemail, external numbers, other AAs). Its scheduling engine — business hours, after hours, holidays — makes it the standard 'front door'. AAs do not queue: they hand the caller somewhere immediately. Design depth comes from the menu tree and the schedule matrix.

- Separate business-hours and after-hours menus; holiday schedule overrides both.
- Nest sparingly: 2 levels max is the usability rule of thumb in designs.
- Each key → any destination, including another location's queue.
- Caller-ID name tagging shows agents which menu path the caller took.

**Worked example.** Clinic design: main number → AA. Business hours: 1→Appointments queue, 2→Billing queue, 3→Nurse hunt group, 0→reception. After hours: greeting + 1→on-call answering service (external PSTN), else→voicemail. Holiday schedule: closed greeting. The whole tree plus schedules fits one diagram — exactly what a Design exhibit shows, with one wrong edge to find.

**Exam angle.** Exhibit items hide errors like a holiday schedule missing or after-hours routing to a daytime-only queue.

### Topic 3 · Call Queue design: distribution, overflow, callback

A queue holds callers and feeds them to agents by a distribution policy: circular (round-robin), top-down (fixed order), longest-idle (fairness), simultaneous (all ring), weighted (percentages). While waiting: welcome message, comfort messages, hold music, position/wait-time announcements. Bounded by overflow rules — max queue size and max wait time — which send excess callers to an alternate destination. Callback lets a caller keep their place and be called when an agent frees.

- Policy follows the requirement's fairness/SLA wording — 'fair share' = longest-idle.
- Overflow: size AND time limits, each with a destination (VM, AA, external).
- Callback threshold (e.g., >5 min) — keeps abandonment metrics down.
- Members can be users, workspaces, virtual lines — across locations.

**Worked example.** 15-agent desk: longest-idle (fairness clause), queue size 10, overflow >10 → voicemail; max wait 15 min → after-hours AA; callback offered at >5 min estimated wait; whisper announcement tells agents 'support line'. Every number traces to a requirement sentence — that traceability is what separates a model answer from a plausible one.

**Exam angle.** Given an SLA paragraph, pick policy + overflow + callback settings; every setting must trace to a sentence.

### Topic 4 · Supervision & analytics — without buying a contact center

Group Call Management (GCM) queues include a supervisor role: monitor (listen silently), whisper (speak to agent only), barge (join the call), plus queue analytics and reports in Control Hub. This covers 'team lead oversight' requirements at zero extra platform cost. The boundary: when requirements say omnichannel (chat/email), CRM screen-pop, IVR flows with logic, skills-based routing across hundreds of agents, or workforce optimization — you've left GCM and entered Webex Contact Center (module D8).

- Supervisor verbs: monitor / whisper / barge — match them to requirement verbs.
- Analytics: queue stats, agent stats, abandonment — Control Hub native.
- GCM ceiling: voice-only, no flows/CRM/omnichannel/WFO.
- Write the dismissal: 'WxCC not required because…' scores points.

**Worked example.** 'Team lead must listen to new hires and coach them live without the caller hearing' → GCM queue + supervisor with monitor + whisper. Nothing in the requirement mentions chat, CRM, or IVR logic → explicitly dismiss WxCC as over-design. Reverse case: add 'and respond to WhatsApp messages' and the answer flips to D8's platform in one sentence.

**Exam angle.** The discriminator list (omnichannel/CRM/flows/skills/WFO) is the test: zero hits = GCM; any hit = contact center.

### Topic 5 · Boundaries & licensing feasibility

Two final checks make a routing design defensible. Boundaries: hunt groups have distribution policies but no queuing, no schedules, no analytics; shared line groups are device-line constructs, not routing logic. Licensing: Webex Calling features differ by license type (e.g., Professional vs Workspace; add-ons for some roles) — a design that assigns supervisor duties or executive features to users whose license doesn't carry them fails feasibility even if the routing logic is perfect.

- Hunt group: instant distribution only — cite the missing capability when dismissing.
- Shared Line Group: appearance/coverage, not call treatment.
- Check the license matrix for: queues membership, supervisor, exec/assistant, analytics access.
- Workspaces (common-area devices) carry different entitlements than users.

**Worked example.** Feasibility catch: a design puts 40 lobby phones (Workspace licenses) as members of a call queue and makes one of them a 'supervisor'. Check the matrix: workspaces can be queue members, but supervisor functions belong to licensed USERS — the lobby-phone supervisor is invalid. One matrix lookup kills the option; that lookup is the skill being tested.

**Exam angle.** At least one answer option per routing item is license-infeasible. Eliminate it first and say why.

## Decide fast — requirement → design answer

| When the brief says… | The design answer is… |
|---|---|
| IVR menu + schedules | Auto Attendant |
| Hold + announcements + callback | Call Queue |
| Lead listens/coaches live | Queue + Supervisor role |
| Simple team ring, no metrics | Hunt Group |
| Omnichannel / CRM / flows | Webex Contact Center (D8) |

## Worked design scenario

**The customer ask.** A 15-agent support desk: callers pick sales or support from a menu during business hours, wait with announcements (max 10 in line), get callback if wait exceeds 5 minutes, and a team lead must silently monitor and whisper-coach new hires. Weekly answer-time reports go to management.

**The model answer.**

- AA on the main number: business/after-hours/holiday schedules; 1→Sales queue, 2→Support queue.
- Queues: longest-idle, size 10 → overflow voicemail, callback at >5 min, comfort + position announcements.
- Team lead = queue supervisor (monitor + whisper); reports from Control Hub queue analytics.
- Licensing pass: agents Professional, lead supervisor-capable; lobby devices excluded from supervision.
- Explicit dismissals: hunt group (no queuing/reports), WxCC (no omnichannel/CRM requirement).

## Check yourself — exam-style questions

_Multiple-answer (select all that apply). Try each in ~2 minutes before revealing the key._

**Q1. Callers must hear their queue position and be offered callback. Which construct and which two settings deliver it?**

<details><summary>Answer key</summary>

- ✅ A Call Queue
- ✅ Position / estimated-wait announcements enabled
- ✅ Callback offered from the queue
- ⬜ A hunt group

</details>

**Q2. When is a hunt group the better answer than a queue? Name the capability boundary that decides.**

<details><summary>Answer key</summary>

- ✅ Distribute calls immediately with simple policies (circular, top-down, etc.)
- ⬜ Callers must wait with music/announcements/callback
- ⬜ Use it when a waiting room and queue position are required
- ✅ A hunt group has no queue / announcements / callback

</details>

**Q3. Which constructs accept members from another location — and which one does not?**

<details><summary>Answer key</summary>

- ✅ Call Queues
- ✅ Hunt Groups
- ✅ Shared Line Groups
- ⬜ Auto Attendant

</details>

**Q4. A design assigns supervisor duties to a workspace-licensed device. Why does it fail, and what check catches it?**

<details><summary>Answer key</summary>

- ✅ Supervisor functions are user-level, tied to a user licence
- ✅ A workspace-licensed device cannot hold supervisor capabilities
- ✅ A licence / role audit catches it
- ⬜ Workspace devices natively support silent monitor and barge

</details>

---
_Source of truth: anchor every answer to the authoritative Cisco document. See the item YAML for source URLs. Part of **CollabForge** — the CCIE Collaboration Design-item bank._