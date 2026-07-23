# D15 · Collab Apps: Voicemail, IM&P, Mobility & Recording Design

> **Blueprint domain:** Domain 7 — Collaboration Apps & Services  ·  **Item type coverage:** scenario Q&A

**After this item you can:**

- Integrate Unity Connection voicemail with correct ports, partitions and routing rules.
- Design on-prem IM&P/Jabber presence and federation building blocks.
- Choose the right mobility feature: SNR, Extension Mobility, Extend & Connect, Device Mobility.
- Select a call-recording architecture: built-in bridge, SIPREC, network-based, Media Proxy.

## Concepts & theory

_Read each topic in three passes — the **concept**, the **worked example**, the **exam angle** — then close the page and re-derive the design rule from memory._

### Topic 1 · Unity Connection voicemail integration

Unity Connection integrates with UCM over a SIP trunk (or SCCP ports) plus a voicemail pilot, profile and hunt/port design. Call and directory handlers, routing rules and partitions/search spaces steer callers to the right greeting and mailbox.

- Voicemail pilot + profile + MWI design must match the trunk integration.
- Direct vs forwarded routing rules pick greeting/mailbox from the redirecting (diverting) number.
- Partitions/CSS in Unity mirror UCM class-of-service for callers and subscribers.

**Worked example.** Forwarded callers hit the opening greeting instead of a mailbox. Unity's forwarded routing rule was not reading the diverting number; aligning the SIP redirect header and the rule sends callers to the right mailbox.

**Exam angle.** 'Wrong greeting / no mailbox match' ties Unity routing rules to the diverting-number header (links to D9).

### Topic 2 · On-prem IM&P and Jabber

Cisco IM&P provides presence and IM for Jabber, integrated with UCM (presence gateway, SIP trunk) and LDAP. Jabber service discovery finds IM&P, UCM and voicemail; federation extends presence to other domains.

- Jabber discovery: _cisco-uds / _collab-edge SRV → UDS/IM&P/voicemail config.
- Presence gateway + SIP trunk between UCM and IM&P drive phone presence.
- Inter-domain federation (SIP/XMPP) extends presence externally via Expressway.

**Worked example.** Jabber shows phone presence but not on-call status. The UCM↔IM&P presence gateway/SIP trunk was missing; adding it lights up on-the-phone presence.

**Exam angle.** Presence gaps map to the IM&P↔UCM integration (gateway/trunk), discovery maps to SRV records.

### Topic 3 · Mobility: SNR, Extension Mobility, Extend & Connect, Device Mobility

Each mobility feature solves a different need. Single Number Reach (Mobile Connect) rings a remote phone; Extension Mobility roams a user's profile to any phone; Extend & Connect controls a non-Cisco phone; Device Mobility adapts roaming device settings by physical location.

- SNR/Mobile Connect: one number rings desk + mobile via a remote destination.
- Extension Mobility: login/logout to apply a device profile (hot-desking).
- Device Mobility: device pool/CSS adapt by IP subnet (roaming laptops/softphones).

**Worked example.** A hot-desking floor needs users' DNs to follow them. Extension Mobility with device profiles + a service URL lets users log into any phone and get their line, CSS and speed dials.

**Exam angle.** Match the mobility feature to the requirement; SNR vs EM vs Device Mobility is the classic distractor set.

### Topic 4 · Call recording architectures

Recording can be done at the phone (built-in bridge forks media to a recorder), via SIPREC (the session border/CUBE forks a standards-based recording session), network-based, or through the CUBE Media Proxy. Choice depends on where media is anchored and compliance scope.

- Built-in bridge (BiB): phone forks media to the recorder — endpoint-anchored, needs supported phones.
- SIPREC on CUBE: standards-based fork at the edge — ideal for trunk-side, carrier-grade recording.
- CUBE Media Proxy centralizes media forking; secure recording adds SRTP to the recorder.

**Worked example.** A contact center must record all PSTN calls regardless of endpoint. SIPREC on CUBE forks every trunk call to the recorder, independent of phone type — cleaner than BiB on each device.

**Exam angle.** Recording items hinge on media anchor: endpoint (BiB) vs trunk/edge (SIPREC/Media Proxy).

### Topic 5 · Webex Bot from a Python skeleton

The blueprint requires implementing a Webex bot from a provided Python skeleton. A bot is a machine identity (bot token) that uses the Webex REST API and webhooks to receive events and post messages — automation without impersonating a user.

- Bot token authenticates the bot; webhooks deliver message/room events.
- Use least-privilege scopes; never ship a personal access token (12-hour, human identity).
- Typical loop: webhook → fetch message → act via REST → post response.

**Worked example.** Given a skeleton, wire a webhook to the bot, parse the incoming message, call the REST API to post a reply — the same token/scope discipline from the API module (D2) applies.

**Exam angle.** Bot items test token model + webhook event flow, not heavy coding — reuse the D2 API security reasoning.

## Decide fast — requirement → design answer

| When the brief says… | The design answer is… |
|---|---|
| Forwarded caller to right mailbox | Unity routing rule + diverting number |
| Jabber on-the-phone presence | UCM↔IM&P presence gateway/trunk |
| One number rings desk + mobile | Single Number Reach (Mobile Connect) |
| Hot-desking, DN follows user | Extension Mobility profile |
| Record all PSTN calls, any phone | SIPREC on CUBE (trunk-anchored) |

## Worked design scenario

**The customer ask.** A customer needs voicemail that routes forwarded callers correctly, Jabber presence including on-call state, hot-desking, single-number reach for field staff, and compliant recording of all PSTN calls. Design the application layer.

**The model answer.**

- Integrate Unity Connection with matching pilot/profile/MWI and forwarded routing rules that read the diverting number (ties to D9 headers).
- Deploy IM&P with the UCM presence gateway/SIP trunk and SRV-based Jabber discovery so phone and on-call presence work.
- Use Extension Mobility for hot-desking and Single Number Reach for field staff — matched to each need, not one feature for all.
- Record PSTN calls with SIPREC on CUBE (trunk-anchored, any endpoint) and secure the recording leg with SRTP.

## Check yourself — exam-style questions

_Multiple-answer (select all that apply). Try each in ~2 minutes before revealing the key._

**Q1. Field staff need their desk number to also ring their mobile, with one caller ID and seamless pull. Which feature, and what object carries the mobile?**

<details><summary>Answer key</summary>

- ✅ Single Number Reach (Mobile Connect)
- ✅ A Remote Destination carries the mobile number
- ✅ It rings desk and mobile in parallel with the enterprise identity
- ⬜ Extension Mobility

</details>

**Q2. Compliance requires recording every PSTN call regardless of phone model. Which recording architecture fits best and why not built-in bridge?**

<details><summary>Answer key</summary>

- ✅ SIPREC on CUBE forks every trunk call to the recorder
- ✅ It is endpoint-agnostic (works for any phone model)
- ✅ Recording follows the trunk media anchor
- ⬜ Built-in bridge (BiB) on every phone

</details>

**Q3. Jabber shows availability but never 'On the phone' when users are on a call. Which integration is missing?**

<details><summary>Answer key</summary>

- ✅ The UCM ↔ IM&P presence gateway + SIP trunk
- ✅ It publishes phone (on-call) state into the presence engine
- ✅ Availability works from IM&P alone; device presence needs UCM
- ⬜ Re-checking LDAP or DNS

</details>

**Q4. You must implement a Webex bot from a provided Python skeleton. What identity and event model does it use, and which token must never be used in production?**

<details><summary>Answer key</summary>

- ✅ A bot token (machine identity) calling the Webex REST API
- ✅ Webhooks deliver room / message events the bot reacts to
- ✅ Use least-privilege scopes
- ⬜ A personal access token shipped in production

</details>

---
_Source of truth: anchor every answer to the authoritative Cisco document. See the item YAML for source URLs. Part of **CollabForge** — the CCIE Collaboration Design-item bank._