# D10 · Media Negotiation & Path Optimization Design

> **Blueprint domain:** Domain 1 — Protocols & APIs  ·  **Item type coverage:** scenario Q&A

**After this item you can:**

- Distinguish early-offer, delayed-offer and early-media and force EO where it matters.
- Read an SDP offer/answer exchange and predict the negotiated codec and media address.
- Design ICE/TURN/STUN so Webex and MRA endpoints pick the optimal media path.
- Choose the correct SRTP interworking mode (pass-through vs SRTP↔RTP) on CUBE.

## Concepts & theory

_Read each topic in three passes — the **concept**, the **worked example**, the **exam angle** — then close the page and re-derive the design rule from memory._

### Topic 1 · SDP offer/answer: early offer, delayed offer, early media

SDP negotiates media via an offer and an answer. Early offer puts SDP in the INVITE; delayed offer sends INVITE with no SDP and the callee offers in the 200. Early media is audio that flows before the 200 (ringback, announcements) via 183 Session Progress.

- Always design SIP trunks to UCM/ITSP for early offer — delayed offer breaks many carriers and delays cut-through.
- UCM 'Early Offer support for voice and video calls' (MTP-less, best-effort) is the preferred trunk setting.
- Early media needs PRACK/100rel so the 183+SDP is acknowledged before audio.

**Worked example.** Callers hear no ringback to an ITSP. UCM used delayed offer; the carrier expected early offer and sent no early media. Enabling EO (MTP-less) on the trunk restores cut-through and ringback.

**Exam angle.** A 'no ringback / clipped first word' symptom on a trunk is an early-offer vs delayed-offer design choice.

### Topic 2 · Payload-type and codec negotiation

Each side lists codecs in preference order; the answerer picks. Dynamic payload types (96–127) are negotiated per leg and need not match across legs. Region/location settings cap UCM codec selection.

- Order in the offer = preference; design the region to put the intended codec first (e.g., G.711 on-net, G.729/OPUS over WAN).
- A common-codec failure returns 488; an MTP/transcoder bridges only when no common codec exists.
- OPUS and AAC-LD widen interop but verify endpoint and CUBE support before relying on them.

**Worked example.** Video calls drop to audio across a WAN. The region set capped video bandwidth below the endpoint's minimum; raising the inter-region video call bit rate (or adding a transcoder) restores video.

**Exam angle.** Region/location bandwidth is the hidden lever behind most 'codec downgraded' exhibits.

### Topic 3 · ICE, STUN and TURN for media path optimization

ICE lets endpoints discover the best media path by gathering candidates (host, server-reflexive via STUN, relayed via TURN) and running connectivity checks. The pair with the lowest latency that passes wins.

- STUN discovers the public mapping (server-reflexive candidate); TURN relays media when direct/NAT-hairpin paths fail.
- Webex Calling and MRA use ICE so on-net calls stay local and only fall back to a relay when necessary.
- Expressway / Webex media nodes act as TURN relays at the edge; size them for worst-case relayed flows.

**Worked example.** Two Webex App users in the same office relay media through the cloud, wasting WAN. ICE host candidates were blocked by an ACL, so only the relayed TURN candidate survived. Opening intra-site UDP lets ICE pick the direct path.

**Exam angle.** 'Media takes a long path between two local users' = ICE candidate blocked; the fix is enabling host/srflx reachability, not adding bandwidth.

### Topic 4 · Media protocols: RTP/RTCP, SRTP, BFCP and ActiveControl (iX)

RTP carries media; RTCP carries quality stats (jitter, loss, RTT). SRTP encrypts RTP/RTCP. BFCP negotiates the presentation (content) channel; ActiveControl (iX, over SIP) carries in-meeting roster/control between UCM and Webex/CMS.

- RTCP receiver reports are the data behind endpoint media metrics and Control Hub quality troubleshooting.
- BFCP can run over UDP or TCP; a blocked BFCP port = 'can't share screen' while audio/video are fine.
- iX (ActiveControl) must be allowed end-to-end or interop meetings lose roster / layout control.

**Worked example.** Screen share fails between UCM endpoints and a CMS conference while voice and video work. BFCP was blocked on the SIP trunk's media range; permitting BFCP restores content sharing.

**Exam angle.** Isolate the failing media stream: audio OK + video OK + share dead points at BFCP, not codecs.

### Topic 5 · SRTP interworking on CUBE: pass-through vs SRTP↔RTP

At the edge, encryption rarely matches end-to-end. CUBE offers SRTP pass-through (transparently relays encrypted media without decrypting), SRTP↔RTP interworking (decrypt one side, clear on the other) and SRTP↔SRTP (re-encrypt with different keys).

- Pass-through keeps CUBE out of the crypto path — lowest CPU, but both ends must use compatible SRTP.
- SRTP↔RTP is for a secure enterprise side meeting a clear-text provider; CUBE becomes the crypto boundary and needs DSP only if it also transcodes.
- Secure trunks need matching TLS for signalling before SRTP for media — crypto must be end-to-end consistent.

**Worked example.** Enterprise endpoints use SRTP but the ITSP is RTP-only. Configure SRTP↔RTP interworking on the provider-facing dial-peer so internal media stays encrypted to CUBE and clear only on the carrier leg.

**Exam angle.** Match the interworking mode to the two sides' crypto capability; choosing pass-through when one side is clear-text is the trap.

## Decide fast — requirement → design answer

| When the brief says… | The design answer is… |
|---|---|
| SIP trunk to ITSP/UCM | Early Offer (MTP-less, best-effort) |
| No common codec exists | Insert transcoder/MTP only then |
| Two local users relay via cloud | Fix ICE host candidate reachability |
| Screen share fails, AV works | Allow BFCP on media range |
| Secure enterprise ↔ clear ITSP | SRTP↔RTP interworking on CUBE |

## Worked design scenario

**The customer ask.** A new ITSP trunk has no ringback, occasional codec-mismatch failures, and the enterprise mandates encrypted internal media though the carrier is RTP-only. Design media negotiation and the edge crypto boundary.

**The model answer.**

- Enable Early Offer (MTP-less) on the UCM and CUBE trunks so SDP is present in the INVITE and ringback/early media cut through.
- Order codecs by region so a common codec is always offered first; reserve transcoder resources only for the genuine no-common-codec case.
- Terminate SRTP at CUBE with SRTP↔RTP interworking on the carrier-facing dial-peer; keep TLS+SRTP on the enterprise side.
- Document RTCP/Control-Hub monitoring and the BFCP/iX port policy so content and roster survive the design.

## Check yourself — exam-style questions

_Multiple-answer (select all that apply). Try each in ~2 minutes before revealing the key._

**Q1. Callers to a new ITSP hear silence instead of ringback and the first word is clipped. Which media-negotiation design choice fixes this and why?**

<details><summary>Answer key</summary>

- ✅ Force Early Offer (MTP-less) on the trunk
- ✅ SDP in the INVITE lets the carrier send 183 early media
- ✅ Delayed offer defers media to the 200/ACK, so no early media
- ⬜ Add an MTP to 'fix' the audio

</details>

**Q2. Two Webex App users in the same building have their media relayed through the cloud. What ICE concept explains this and what is the fix?**

<details><summary>Answer key</summary>

- ✅ ICE could not validate the direct (host / server-reflexive) candidate
- ✅ Permit intra-site UDP so host candidates succeed
- ✅ ICE always picks the lowest-latency passing pair
- ⬜ Add WAN bandwidth / a larger TURN relay

</details>

**Q3. Audio and video work between a UCM endpoint and a CMS conference, but screen sharing fails. Which protocol is blocked and how do you know it is not a codec problem?**

<details><summary>Answer key</summary>

- ✅ BFCP (the content / floor-control channel) is blocked
- ✅ Audio and video negotiate on separate m-lines, isolating the fault
- ✅ BFCP can run over UDP or TCP and be filtered independently
- ⬜ Renegotiate the voice codec or add a transcoder

</details>

**Q4. The enterprise requires encrypted media internally but the ITSP is RTP-only. Which CUBE interworking mode meets both, and what would pass-through do here?**

<details><summary>Answer key</summary>

- ✅ SRTP ↔ RTP interworking on the provider-facing dial-peer
- ✅ CUBE becomes the crypto boundary (SRTP inside, RTP to carrier)
- ⬜ SRTP pass-through
- ⬜ Leave enterprise media unencrypted end to end

</details>

---
_Source of truth: anchor every answer to the authoritative Cisco document. See the item YAML for source URLs. Part of **CollabForge** — the CCIE Collaboration Design-item bank._