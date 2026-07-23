# D12 · CUBE Dial-Peers, Normalization & Survivability Design

> **Blueprint domain:** Domain 3 — Call Control & Dial Plan  ·  **Item type coverage:** scenario Q&A

**After this item you can:**

- Predict inbound and outbound dial-peer matching order on IOS-XE CUBE.
- Shape digits and headers with voice translation rules and SIP/SDP normalization (Lua).
- Use dial-peer groups, server groups and E.164 pattern maps for scalable routing.
- Design SIP-SRST and the Webex Calling Survivability Gateway for branch survivability.

## Concepts & theory

_Read each topic in three passes — the **concept**, the **worked example**, the **exam angle** — then close the page and re-derive the design rule from memory._

### Topic 1 · Inbound vs outbound dial-peer matching

CUBE selects one inbound dial-peer (to apply ingress policy) and then an outbound dial-peer (to route). Inbound matching uses, in order, incoming uri / called / calling / port; outbound uses destination-pattern or dest server/dpg. Missing the order causes the wrong policy to apply.

- Prefer 'incoming uri' / 'incoming called-number' for deterministic inbound matching over relying on port.
- Most-specific destination-pattern wins outbound; use dial-peer groups to escape longest-match guesswork.
- dial-peer 0 (default) means you matched nothing you intended — always define explicit peers.

**Worked example.** Calls hit the wrong codec/SIP profile because the implicit inbound peer matched. Adding 'incoming called-number' on the intended peer makes ingress policy deterministic.

**Exam angle.** 'Wrong profile/codec applied inbound' is an inbound dial-peer matching order question.

### Topic 2 · Voice translation rules and profiles

Translation rules use regex (/match/replace/) to re-write calling/called numbers; a translation-profile bundles rules and is applied to a dial-peer or voice-port for incoming or outgoing direction.

- Order of rules matters — first match wins within a rule set.
- Apply profiles directionally (translate calling vs called, incoming vs outgoing) and on the correct peer.
- Use them for +E.164 normalization, DID expansion and CLID manipulation at the edge.

**Worked example.** An ITSP delivers 10-digit DIDs but UCM expects +E.164. An incoming translation profile prepends +1, so UCM routing sees a clean globalized number.

**Exam angle.** Digit-manipulation items specify direction and peer — applying the rule on the wrong side is the trap.

### Topic 3 · SIP/SDP normalization and transparency (Lua)

SIP profiles (and Lua normalization scripts) add, remove or rewrite SIP headers and SDP to fix interop quirks; transparency passes unknown headers through unchanged. They are the surgical tool when a carrier deviates from standards.

- IOS-XE SIP profiles edit request/response headers per peer or globally.
- Lua scripts handle complex conditional rewrites beyond static SIP profiles.
- Prefer the least-invasive fix; over-normalizing hides the real interop issue.

**Worked example.** A carrier rejects calls because of an unexpected Diversion header format. A SIP profile rewrites that header on the outbound peer, and the calls complete without touching UCM.

**Exam angle.** When only one carrier breaks and standards are met, the answer is a SIP profile / Lua normalization at CUBE.

### Topic 4 · Dial-peer groups, server groups and E.164 pattern maps

Server groups list multiple target IPs for redundancy on one dial-peer; E.164 pattern maps attach many destination patterns to one dial-peer; dial-peer groups (DPG) bind a chosen outbound group to an inbound peer, removing longest-match ambiguity.

- Destination server-group = built-in failover/round-robin to multiple UCM subscribers.
- E.164 pattern map = one peer, many patterns — cleaner than dozens of peers.
- DPG ties 'calls that came in here go out via this group', deterministic and scalable.

**Worked example.** Trunk failover to a second UCM subscriber was manual. A destination server group with two IPs gives automatic re-route on SIP options out-of-service, no extra dial-peers.

**Exam angle.** Scaling/failover items favour server groups, pattern maps and DPGs over many discrete dial-peers.

### Topic 5 · Branch survivability: SIP-SRST & Webex Calling Survivability GW

When the WAN/cloud is down, branch phones must keep dialing. SIP-SRST on an IOS-XE gateway registers local SIP phones and provides basic call routing during UCM outage; the Webex Calling Survivability Gateway does the same for Webex Calling registered devices.

- SRST scope is deliberately basic: local + PSTN calling, reduced features, automatic fallback/recovery.
- Size SRST for the branch device count and define the PSTN breakout it uses while isolated.
- Webex Calling Survivability Gateway (IOS-XE) keeps WxC phones calling locally during a cloud/Internet outage.

**Worked example.** A branch loses its WAN; phones re-home to SRST and can still call locally and to PSTN. On WAN recovery they re-register to UCM automatically — design the SRST reference and CSS so day-to-day routing is unchanged.

**Exam angle.** Survivability items test scope and fallback: SRST is intentionally feature-reduced, not a UCM replacement.

## Decide fast — requirement → design answer

| When the brief says… | The design answer is… |
|---|---|
| Deterministic inbound policy | Match 'incoming called/uri', not port |
| Normalize ITSP DIDs to +E.164 | Incoming voice translation profile |
| One carrier breaks a header | SIP profile / Lua normalization |
| Trunk failover to 2nd UCM sub | Destination server group |
| Branch keeps calling in WAN outage | SIP-SRST / WxC Survivability GW |

## Worked design scenario

**The customer ask.** A new ITSP delivers 10-digit DIDs, rejects calls over one non-standard header, and the branch must keep dialing during WAN outages. The current config relies on implicit dial-peers and manual subscriber failover. Redesign the CUBE edge.

**The model answer.**

- Make inbound matching explicit ('incoming called-number'/uri) so the right SIP profile and codec apply; route outbound with a dial-peer group.
- Normalize DIDs to +E.164 with an incoming translation profile and fix the carrier header with a targeted SIP profile — least-invasive.
- Add a destination server group across UCM subscribers for automatic failover via SIP OPTIONS keepalives.
- Deploy SIP-SRST (or WxC Survivability Gateway) sized for the branch, with local + PSTN routing and automatic recovery.

## Check yourself — exam-style questions

_Multiple-answer (select all that apply). Try each in ~2 minutes before revealing the key._

**Q1. Inbound calls on CUBE get the wrong SIP profile and codec. Explain the matching behaviour and the fix.**

<details><summary>Answer key</summary>

- ✅ Add 'incoming called-number' / uri for deterministic ingress matching
- ✅ Inbound order: incoming uri → called → calling → port
- ✅ With nothing explicit, the implicit default peer applies its policy
- ⬜ Edit the outbound dial-peer to fix the ingress profile

</details>

**Q2. Only one carrier rejects calls, and your SIP signalling is standards-compliant. What is the right tool and the design caution?**

<details><summary>Answer key</summary>

- ✅ A SIP profile (or Lua) on the carrier-facing dial-peer
- ✅ Make the smallest change that fixes interop
- ✅ Normalization confines the carrier quirk to CUBE
- ⬜ Change UCM-wide settings to satisfy one carrier

</details>

**Q3. You need automatic trunk failover across two UCM subscribers from a single dial-peer. Which CUBE construct provides it and how is health detected?**

<details><summary>Answer key</summary>

- ✅ A destination server group listing both subscriber IPs
- ✅ SIP OPTIONS keepalive marks a down target out-of-service
- ✅ Server groups avoid proliferating dial-peers
- ⬜ A second dial-peer with higher preference but no liveness check

</details>

**Q4. During a WAN outage branch phones must still place local and PSTN calls. What provides this and what is the explicit scope limitation?**

<details><summary>Answer key</summary>

- ✅ SIP-SRST (or the WxC Survivability Gateway) registers local phones
- ✅ Scope is intentionally basic — local + PSTN, reduced features
- ✅ Automatic fallback and recovery on WAN restore
- ⬜ SRST provides full UCM feature parity during the outage

</details>

---
_Source of truth: anchor every answer to the authoritative Cisco document. See the item YAML for source URLs. Part of **CollabForge** — the CCIE Collaboration Design-item bank._