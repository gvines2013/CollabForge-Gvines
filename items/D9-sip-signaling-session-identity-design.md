# D9 · SIP Signaling & Session Identity Design

> **Blueprint domain:** Domain 1 — Protocols & APIs  ·  **Item type coverage:** scenario Q&A

**After this item you can:**

- Read a SIP ladder and name every request, response class and the dialog it builds.
- Predict caller-ID and privacy outcomes from identity, Diversion and P-A-I headers.
- Use Route / Record-Route to explain why a proxy stays in the path — or drops out.
- Correlate a call across UCM, CUBE and Webex using Call-ID, Session-ID and Cisco-GUID.

## Concepts & theory

_Read each topic in three passes — the **concept**, the **worked example**, the **exam angle** — then close the page and re-derive the design rule from memory._

### Topic 1 · SIP transactions, dialogs and the request/response model

SIP is a text request/response protocol. A method (INVITE, ACK, BYE, CANCEL, REGISTER, SUBSCRIBE, NOTIFY, REFER, UPDATE, INFO) starts a transaction; responses are grouped 1xx provisional, 2xx success, 3xx redirect, 4xx client error, 5xx server error, 6xx global failure.

- A dialog is identified by Call-ID + local tag + remote tag; INVITE/200/ACK establishes it, BYE tears it down.
- CANCEL only stops a still-ringing INVITE; after a 200 OK you must use BYE.
- 100rel/PRACK makes a 18x reliable so early media and 183 Session Progress are acknowledged.

**Worked example.** A trace shows INVITE → 100 → 180 → 200 → ACK → … → BYE → 200. You can immediately tell the dialog matched, media flowed, and the caller hung up. A 488 instead of 200 means 'not acceptable here' — almost always an SDP/codec or SRTP mismatch, not a routing problem.

**Exam angle.** Items hide the fault in a single response code — map the 4xx/5xx to the layer (488 = media, 403 = policy, 404 = dial-plan) before troubleshooting.

### Topic 2 · Identity headers: From, P-Asserted-Identity and Privacy

Calling-party identity travels in several headers. From is user-supplied and untrusted; P-Asserted-Identity (PAI) carries the network-verified identity inside a trusted domain; Privacy: id requests that PAI be withheld from the far end.

- UCM sends PAI (and optionally RPID) on trunks; the SIP profile / trunk config decides which header the provider trusts.
- Privacy header + 'Calling Line ID Presentation = Restricted' drive CLIR; the trunk must honour it or you leak identity.
- Number vs name vs URI are independent fields — a design states each one's source and transformation.

**Worked example.** An ITSP shows the corporate main number on every outbound call. Root cause: UCM presents the DN in PAI but the carrier bills on From, which an external-phone-number-mask left blank. Fix in the SIP profile / transformation, not on the phone.

**Exam angle.** Watch for a requirement that says 'present the main number but keep the real DID in the network' — that is PAI vs From by design.

### Topic 3 · Route, Record-Route and Via — who stays in the path

Via traces the request hop-by-hop for responses. Record-Route lets a proxy insert itself so every in-dialog message (BYE, re-INVITE) keeps traversing it; Route headers then force the pre-built path.

- A proxy that wants to stay for the whole call adds Record-Route; one that only needs the INVITE does not.
- Loose routing (;lr) is the modern default — the Request-URI stays the target, Route headers steer.
- Max-Forwards decrements per hop; loops surface as 483 Too Many Hops.

**Worked example.** Mid-call hold fails only on transferred calls. The transfer moved media but a stateful SBC dropped out because it never Record-Routed, so the re-INVITE bypassed it and hit a firewall pinhole that no longer existed.

**Exam angle.** If in-dialog requests fail but call setup works, suspect a missing Record-Route on a box you assumed was anchored.

### Topic 4 · Diversion vs History-Info — carrying the redirect reason

When a call is forwarded, the original and intermediate targets must be conveyed so voicemail, billing and loop-prevention work. Diversion (legacy) and History-Info (RFC 4244) both carry this.

- Voicemail systems read the diverting number to pick the right mailbox — drop it and callers land in the wrong greeting.
- UCM can be set to send Diversion, History-Info, or both per SIP trunk / profile; the provider dictates which.
- Redirecting reason codes (user-busy, no-answer, unconditional) drive CFB vs CFNA mailbox behaviour.

**Worked example.** Forward-to-Unity calls reach a generic greeting. Unity needs the original called number; the trunk was sending History-Info but Unity was configured to read Diversion. Align the header, mailbox routing works.

**Exam angle.** A 'wrong mailbox' or 'no redirected number' symptom is a Diversion / History-Info selection question, not a Unity bug.

### Topic 5 · Correlating a call: Call-ID, Session-ID and Cisco-GUID

Call-ID is unique per SIP dialog, so each leg of a multi-hop call has a different Call-ID. Session-ID (RFC 7989) is an end-to-end identifier that survives B2BUA hops; Cisco-GUID ties IOS-XE/CUBE legs together.

- To follow a call UCM → CUBE → ITSP you correlate on Session-ID, not Call-ID, because CUBE re-originates the dialog.
- Session-ID appears as local/remote UUID pair and is logged by UCM, CUBE and Webex for cross-platform tracing.
- Cisco-GUID / peer-callid in 'show call active voice' stitches inbound and outbound dial-peer legs on the gateway.

**Worked example.** A one-way-audio ticket spans three systems. Filtering each tool by the shared Session-ID UUID isolates the exact leg where SDP showed the wrong media address — minutes instead of hours.

**Exam angle.** Multi-system trace items expect Session-ID as the correlation key; choosing Call-ID is the classic distractor.

## Decide fast — requirement → design answer

| When the brief says… | The design answer is… |
|---|---|
| Network-verified caller ID on a trunk | P-Asserted-Identity (+ Privacy) |
| Hide caller number from far end | Privacy: id + CLIR restricted |
| Keep SBC in path for whole call | Record-Route on the SBC |
| Voicemail needs original called number | Diversion or History-Info (match provider) |
| Trace a call across UCM/CUBE/Webex | Correlate on Session-ID (RFC 7989) |

## Worked design scenario

**The customer ask.** Outbound calls via a new SIP provider show the wrong caller ID, CLIR-restricted calls still display the number, and forwarded-to-voicemail calls reach the wrong greeting. Design the header strategy on the UCM trunk and CUBE.

**The model answer.**

- Present the corporate identity in P-Asserted-Identity and set the billing/From number with an external phone-number mask; document which header the carrier trusts.
- Honour Privacy: id end-to-end — verify the SIP profile does not strip it and the carrier suppresses PAI when restricted.
- Send the redirecting number in the header the provider and Unity both read (Diversion vs History-Info) — align all three.
- State the loop-prevention and correlation plan: Max-Forwards, and Session-ID logging on UCM and CUBE for cross-platform tracing.

## Check yourself — exam-style questions

_Multiple-answer (select all that apply). Try each in ~2 minutes before revealing the key._

**Q1. A trunk must show the network-verified caller identity but let users restrict presentation. Which two headers implement this, and what does each do?**

<details><summary>Answer key</summary>

- ✅ P-Asserted-Identity carries the network-verified identity
- ✅ Privacy: id withholds PAI from the untrusted far end
- ⬜ Use the From header as the trust anchor
- ⬜ Remote-Party-ID removes the need for PAI

</details>

**Q2. Call setup works but mid-call re-INVITEs (hold/transfer) fail at a stateful SBC. What SIP mechanism was almost certainly missing?**

<details><summary>Answer key</summary>

- ✅ Record-Route on the SBC keeps it in every in-dialog message
- ✅ Without Record-Route, in-dialog requests route around the SBC
- ⬜ Via alone keeps the SBC in the dialog
- ⬜ The codec must be renegotiated to fix hold/transfer

</details>

**Q3. You must follow a single call across UCM, CUBE and Webex. Why is Call-ID insufficient, and what do you correlate on instead?**

<details><summary>Answer key</summary>

- ✅ Session-ID (RFC 7989) correlates across B2BUA hops
- ✅ Call-ID is unique per dialog, so it changes at each B2BUA
- ✅ Cisco-GUID stitches the gateway legs together
- ⬜ Filtering every tool by one Call-ID follows the whole call

</details>

**Q4. Forwarded-to-voicemail calls reach a generic greeting instead of the original called user's mailbox. Which header family is misconfigured and why does it matter?**

<details><summary>Answer key</summary>

- ✅ The redirecting-number header (Diversion or History-Info)
- ✅ Unity selects the mailbox from the original called number
- ✅ Align the header Unity reads with what the trunk sends
- ⬜ It is a Unity Connection database fault

</details>

---
_Source of truth: anchor every answer to the authoritative Cisco document. See the item YAML for source URLs. Part of **CollabForge** — the CCIE Collaboration Design-item bank._