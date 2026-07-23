# D3 · QoS & Call Admission Control Design

> **Blueprint domain:** Domain 2 — Infrastructure & QoS  ·  **Item type coverage:** scenario Q&A

**After this item you can:**

- Build the collaboration QoS policy from MQC primitives — and size the LLQ with real math
- Place trust boundaries and state measurable targets per path
- Layer UCM ELCAC and CUBE CAC without double-counting bandwidth

## Concepts & theory

_Read each topic in three passes — the **concept**, the **worked example**, the **exam angle** — then close the page and re-derive the design rule from memory._

### Topic 1 · The MQC model: classify → act → attach

Every IOS-XE QoS design is three building blocks. class-map answers 'which traffic?' (match dscp ef, match access-group, match protocol). policy-map answers 'what happens to it?' (priority = LLQ, bandwidth = CBWFQ guarantee, police, shape, set = re-mark, random-detect = WRED). service-policy attaches the policy to an interface, in or out. Hierarchy nests them: a parent shaper creates back-pressure so a child queuing policy can work on sub-rate circuits.

- class-map = classification only; policy-map = actions; service-policy = attachment.
- priority (LLQ) = strict priority WITH built-in policer — voice can't starve the link.
- bandwidth = minimum guarantee under congestion (CBWFQ), no cap.
- Parent shape + child queue = the standard design for 'carrier gives 50 Mb on a GigE'.

**Worked example.** Skeleton: class-map VOICE match dscp ef / policy-map CHILD class VOICE priority percent 33; class VIDEO bandwidth percent 25 / policy-map PARENT class class-default shape average 50000000, service-policy CHILD / interface Gi0/0/0 service-policy output PARENT. Read it bottom-up in exam diagrams: attachment → shaper → queues.

**Exam angle.** Items show a policy fragment and ask what's wrong — usually a child queue with no parent shaper on a sub-rate circuit.

### Topic 2 · The collaboration marking plan — with LLQ sizing math

Cisco's collaboration QoS model (RFC 4594-based): voice bearer EF/46 into the LLQ; interactive video AF41/34 into a guaranteed CBWFQ class with DSCP WRED; signaling CS3/24 small but protected; meetings/streaming AF31–AF21; scavenger CS1 capped at ~1%. The LLQ is sized with arithmetic, not vibes: busy-hour concurrent calls × per-call bandwidth for the negotiated codec including L3 overhead.

- G.711 ≈ 80 kb/s per call at L3 (64k payload + RTP/UDP/IP); G.729 ≈ 24–26 kb/s.
- LLQ = BHCC × per-call rate + headroom; the priority policer enforces it.
- Video class sized per PA bandwidth tables (resolution/fps dependent).
- Signaling needs little (CS3, e.g., 2–5%) but must never be best-effort.

**Worked example.** Site with 60 staff, BHCC 10 concurrent G.711 calls: LLQ = 10 × 80 kb/s = 800 kb/s → priority 1000 kb/s with headroom. Same site on G.729: 10 × 26 = 260 kb/s. This number must MATCH the ELCAC location bandwidth (topic 4) — when they disagree, admitted calls exceed the queue and every call degrades. That coupling is the exam's favorite trap.

**Exam angle.** Be ready to do the multiplication live and to spot LLQ ≠ CAC mismatches in a two-exhibit item.

### Topic 3 · Trust boundaries, marking points & quality targets

Marking is only trustworthy where you control it. The trust boundary sits at the access edge: the switch extends trust to the phone via LLDP-MED/CDP (voice VLAN, phone marks EF), PCs behind the phone are re-marked to best effort. At WAN ingress you re-classify if site policy differs. Against this you state measurable targets — the numbers a Design-module answer is expected to quote.

- Enterprise voice targets: ≤150 ms one-way latency, ≤30 ms jitter, ≤1% loss.
- Local Gateway → Webex Calling cloud: ≤100 ms one-way, ≤10 ms jitter, ≤0.5% loss.
- LLDP-MED assigns voice VLAN + tells the phone what DSCP to use.
- Conditional trust: trust the phone, not the PC behind it.

**Worked example.** Exam-style exhibit: a site marks all traffic EF at the WAN router 'to be safe'. Why is that wrong? Because the LLQ policer now polices business data along with voice — drops hit everything, and voice loses its protection. Correct: trust boundary at access, EF only for RTP from phones, re-mark everything else.

**Exam angle.** Quote the LGW link targets verbatim (100/10/0.5) — they come straight from the Local Gateway guide and appear in cloud-calling designs.

### Topic 4 · UCM Enhanced Locations CAC + AAR

QoS protects admitted calls; CAC decides whether to admit. ELCAC models the WAN as locations (sites) connected by links, each with audio/video/immersive bandwidth pools. Every call between locations debits the pools; when empty, the call is denied. Denial without a fallback is a user-visible failure — so AAR (Automated Alternate Routing) reroutes the denied call over the PSTN automatically, using globalized +E.164 routing.

- Locations & links = logical topology; LBM (Location Bandwidth Manager) does the accounting.
- Intercluster ELCAC: LBM hub group replicates the topology between clusters.
- AAR needs: AAR groups, AAR CSS on phones, globalized PSTN routes — forget one and reroute silently fails.
- Pool sizes must equal the QoS queue math from topic 2.

**Worked example.** Site A location: audio pool 800 kb/s, calls counted at 80 kb/s (G.711) → 10 concurrent admitted. Call 11: denied by LBM → AAR kicks in → UCM globalizes the called DN to +E.164, routes via the caller's local PSTN gateway. User hears normal ringback, never knows. Without AAR CSS: user hears reorder — and the design item asks why.

**Exam angle.** 'Out of bandwidth, what does the caller experience?' depends entirely on whether AAR is fully designed — the three prerequisites are the answer.

### Topic 5 · CUBE CAC & the layering rule

ELCAC sees the enterprise WAN, but it cannot see the provider trunk or the SBC's own health. CUBE CAC fills that gap with three families: per-dial-peer/tenant max-conn (concurrent call caps), global call thresholds (CPU, memory, total-calls — new calls rejected when the box is hot), and call spike protection (rate limiting INVITE bursts). The layering rule: each layer guards its own segment; never count the same bandwidth twice, and document which layer rejects first.

- max-conn on dial-peer/tenant = contractual trunk cap (e.g., 100 sessions bought).
- call threshold global cpu-avg/total-mem = self-protection under load.
- call spike = absorbs robocall/failover bursts before they hit UCM.
- Rejected at CUBE = SIP 503 to provider; design states the retry/overflow behavior.

**Worked example.** Contract: 100 concurrent PSTN sessions. Config: 'max-conn 100' on the outbound dial-peer (or per tenant), 'call spike 30 size 1000' to absorb bursts, thresholds at cpu-avg 80%. Layering: ELCAC admits a WAN call → CUBE admits it to the trunk → provider takes it. A 101st PSTN call is CUBE's rejection (503/busy-out to alternate trunk), NOT an ELCAC event — exam items ask which layer rejected.

**Exam angle.** Given a failure ('calls fail only to PSTN at peak'), identify the rejecting layer: trunk cap (CUBE) vs WAN pool (ELCAC) vs queue drops (QoS).

## Decide fast — requirement → design answer

| When the brief says… | The design answer is… |
|---|---|
| Sub-rate WAN circuit | Parent shaper + child LLQ/CBWFQ |
| Enterprise WAN admission | ELCAC + AAR (3 prerequisites) |
| Provider trunk cap | CUBE max-conn per dial-peer/tenant |
| INVITE burst / TDoS | Call spike + thresholds |
| LGW → Webex cloud link | ≤100 ms / 10 ms / 0.5% targets |

## Worked design scenario

**The customer ask.** 40-site hub-and-spoke WAN, centralized UCM, video-enabled, 100 contracted PSTN sessions at the hub CUBE. At peak, spoke users report choppy audio and occasional fast-busy to the PSTN.

**The model answer.**

- Per spoke: parent shape to CIR, child policy LLQ sized BHCC × codec rate, AF41 video class, CS3 signaling.
- ELCAC location pools set EQUAL to the LLQ math; AAR groups + AAR CSS + globalized routes for denial reroute.
- Hub CUBE: max-conn 100 (contract), call spike + CPU/memory thresholds; 503 behavior documented.
- Diagnosis mapping: choppy audio = LLQ undersized vs ELCAC pool; fast-busy = trunk cap at CUBE, not WAN CAC.

## Check yourself — exam-style questions

_Multiple-answer (select all that apply). Try each in ~2 minutes before revealing the key._

**Q1. ELCAC admits 12 calls but the LLQ is sized for 10. What do users experience and which design rule was violated?**

<details><summary>Answer key</summary>

- ✅ All 12 calls degrade — the LLQ policer drops EF across every flow
- ✅ Loss is per-packet, so it is distributed across all streams
- ✅ Violated rule: CAC admission math must equal the LLQ queue math
- ⬜ Only calls 11 and 12 will sound bad

</details>

**Q2. Write the three MQC constructs (and hierarchy) for 'guarantee voice priority within a 50 Mb/s service on a GigE'.**

<details><summary>Answer key</summary>

- ✅ Child policy-map: class VOICE / priority <rate>
- ✅ Parent policy-map: class-default / shape average 50 Mb/s with nested child
- ✅ Attach with service-policy output on the GigE
- ⬜ A flat policy with 'priority' attached directly to the GigE

</details>

**Q3. List the three AAR prerequisites without which a CAC denial becomes a reorder tone.**

<details><summary>Answer key</summary>

- ✅ AAR groups assigned (derive the PSTN prefix between sites)
- ✅ An AAR CSS that can reach globalized PSTN route patterns
- ✅ Globalized +E.164 external masks / routing
- ⬜ Enabling the AAR service parameter alone

</details>

**Q4. Why does a correctly designed ELCAC deployment still need CUBE CAC? Name the two things ELCAC cannot see.**

<details><summary>Answer key</summary>

- ✅ The provider trunk's contractual / purchased session limit
- ✅ The SBC platform's own health (CPU, memory, INVITE burst)
- ⬜ The enterprise WAN location bandwidth (ELCAC already models this)
- ⬜ The endpoints' codec preference order

</details>

---
_Source of truth: anchor every answer to the authoritative Cisco document. See the item YAML for source URLs. Part of **CollabForge** — the CCIE Collaboration Design-item bank._