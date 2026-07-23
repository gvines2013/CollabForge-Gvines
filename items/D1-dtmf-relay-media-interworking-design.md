# D1 · DTMF Relay & Media Interworking Design

> **Blueprint domain:** Domain 1 — Protocols & APIs  ·  **Item type coverage:** scenario Q&A, matrix (MX1)

**After this item you can:**

- Explain how each DTMF method actually carries a digit, end to end
- Predict negotiation outcomes on CUBE calls — before looking at a debug
- Design MTP-less call paths and defend them with the interworking rules

## Concepts & theory

_Read each topic in three passes — the **concept**, the **worked example**, the **exam angle** — then close the page and re-derive the design rule from memory._

### Topic 1 · Why DTMF needs 'relay' at all

A key press is just two audio sine waves (e.g., digit 5 = 770 Hz + 1336 Hz). With G.711 those tones survive in the voice stream — 'in-band' works. But low-bitrate codecs like G.729 are built to compress human speech; they distort pure tones, so the far-end IVR hears garbage. The fix: take the digit OUT of the audio and send it as data. That is DTMF relay.

- In-band = tones inside RTP audio. Reliable only with G.711/G.722.
- Relay = digit sent as an event, either in the media plane or the signaling plane.
- Every interop failure is a mismatch between what each leg can send/accept.
- Design rule: never let a G.729/OPUS path depend on in-band tones.

**Worked example.** A bank's IVR works fine on-net (G.711) but fails for branch callers whose WAN calls use G.729. Diagnosis: digits are in-band; G.729 mangles them. Design fix: mandate RFC 2833 relay end-to-end — the codec then no longer matters, because digits travel as named events, not audio.

**Exam angle.** Scenario items hide the codec in a diagram footnote. G.729 + 'IVR ignores digits' = in-band dependency.

### Topic 2 · RFC 2833 / 4733 (rtp-nte): the media-plane method

The digit is sent as a special RTP packet type called a named telephony event (NTE), inside the same RTP stream as the audio but with its own payload type (PT). The PT number is negotiated in SDP: the offer carries a line like 'a=rtpmap:101 telephone-event/8000'. Because the event is data (digit 5, duration, volume), it is codec-independent and survives any voice codec.

- Default PT is 101, but ANY dynamic PT (96–127) is legal — never assume 101.
- Negotiated per leg in the SDP offer/answer; each leg can use a different PT.
- The standard answer for SIP trunking and mandatory toward Webex Calling LGW.
- Redundant transmissions make it robust to packet loss.

**Worked example.** Offer: m=audio 16384 RTP/AVP 0 101 + a=rtpmap:101 telephone-event/8000. Answer from ITSP: a=rtpmap:96 telephone-event/8000. Result: leg A sends digit events on PT 101, leg B expects PT 96 — works only because CUBE rewrites the PT between legs (payload interworking).

**Exam angle.** Trace-reading items show two SDPs with different telephone-event PTs and ask why the call still works.

### Topic 3 · Out-of-band: KPML, SIP INFO, unsolicited NOTIFY

Out-of-band methods move digits into SIP signaling, bypassing media entirely. KPML (RFC 4730) is what Cisco endpoints registered to UCM use: the interested party SUBSCRIBEs to key presses and receives a NOTIFY per digit. SIP INFO sends the digit in an INFO message body. Unsolicited NOTIFY is a legacy Cisco IOS method that sends NOTIFY without subscription.

- KPML = subscription model, per-dialog, precise; Cisco phone default toward UCM.
- SIP INFO = no subscription; mostly demanded by specific providers/apps.
- Unsolicited NOTIFY = legacy IOS gateway interop; avoid in new designs.
- Signaling-plane digits are immune to codec and media-path problems.

**Worked example.** An 8865 on UCM dials an ITSP IVR. The phone produces KPML digits toward UCM; the ITSP only accepts RFC 2833. Nothing is wrong with either side — the DESIGN must place the interworking point (CUBE) between them and state it explicitly: kpml on the UCM leg, rtp-nte on the provider leg.

**Exam angle.** Know which side of the call naturally produces which method: UCM endpoints → KPML; ITSPs → 2833; legacy IOS → NOTIFY.

### Topic 4 · CUBE interworking rules — and the MTP-less goal

CUBE natively interworks any RELAY method with any other relay method (rtp-nte ↔ kpml ↔ notify ↔ info) because both are structured events — no DSP needed. The only expensive case is in-band tone → relay: someone must LISTEN to the audio to detect tones, which requires a DSP/MTP. UCM behaves similarly: if trunk legs can't agree, UCM inserts an MTP — that's a design defect, not a fix.

- Relay ↔ relay: free, signaling/media event translation on CUBE.
- In-band ↔ relay: DSP-backed MTP required — design it out where possible.
- Configure preference: dtmf-relay rtp-nte sip-kpml on the dial-peer; richest common wins.
- PA/SRND goal: MTP-less operation; MTP insertion adds delay, failure points, capacity load.

**Worked example.** Dial-peer config: 'dtmf-relay rtp-nte sip-kpml'. UCM leg negotiates KPML, ITSP leg negotiates rtp-nte; CUBE converts each NOTIFYed digit into an RTP NTE packet. Zero DSPs. If instead the ITSP were in-band-only, the design answer changes: insert a DSP MTP at CUBE AND flag it as a contract exception — push the provider to support 2833.

**Exam angle.** Classic question: 'which design avoids MTP insertion?' Answer = both legs on relay methods + CUBE interworking.

### Topic 5 · Payload-type interworking & codec policy

Two independent negotiations happen per leg: the voice codec and the telephone-event PT. Designs must keep both transcoding-free. Codec policy: constrain offers with codec preference lists so both legs land on the same codec; payload policy: allow asymmetric NTE PTs and let CUBE rewrite them. If the codecs differ per leg, you need a transcoder (DSP); if only the event PT differs, you don't.

- Asymmetric telephone-event PT (101 vs 96) = handled natively by CUBE.
- Different voice codecs per leg = transcoding DSPs — a sizing and cost line-item.
- Codec preference lists on CUBE + UCM regions keep paths transcoder-free.
- Document expected codec + DTMF outcome for every path in the design.

**Worked example.** Design table for path UCM↔CUBE↔ITSP: codec G.711a both legs (region + preference list enforce it), DTMF rtp-nte PT 101 ↔ PT 96 (asymmetric OK). Same table for the Webex LGW path: codec OPUS/G.711 per cloud policy, DTMF rtp-nte mandatory. This per-path table IS the deliverable a Design-module item expects you to recognize as correct.

**Exam angle.** Differentiate: PT mismatch (free fix) vs codec mismatch (DSP cost). Items bait you into 'add a transcoder' for a PT issue.

## Decide fast — requirement → design answer

| When the brief says… | The design answer is… |
|---|---|
| UCM↔CUBE↔ITSP trunk | rtp-nte both legs |
| KPML phones ↔ 2833-only provider | CUBE interworks — no DSP |
| Provider supports in-band only | DSP MTP + contract exception |
| IVR/CVP consumes digits | Out-of-band toward the app |
| Webex Calling Local Gateway | rtp-nte (mandatory) |

## Worked design scenario

**The customer ask.** Calls from older conference phones intermittently fail IVR navigation via a new SIP provider. Traces show the provider answers telephone-event PT 96; UCM endpoints use KPML; conference phones are G.729-capable only.

**The model answer.**

- Keep kpml + rtp-nte offered on the UCM leg, rtp-nte on the provider leg — CUBE interworks, no MTP.
- Enable asymmetric payload interworking so PT 101 ↔ PT 96 is rewritten per leg.
- Root cause for the old phones: they fall back to in-band on G.729 — exclude in-band paths or force relay support.
- State the constraint in the design: no call path may depend on in-band DTMF over compressed codecs.

## Check yourself — exam-style questions

_Multiple-answer (select all that apply). Try each in ~2 minutes before revealing the key._

**Q1. A provider requires SIP INFO for DTMF while UCM endpoints use KPML. Which single device interworks them, and is a DSP required?**

<details><summary>Answer key</summary>

- ✅ CUBE interworks SIP INFO ↔ KPML in software — no DSP required
- ⬜ An MTP or transcoder is required to bridge SIP INFO and KPML
- ⬜ A DSP is mandatory because the two methods differ
- ⬜ UCM converts the methods natively; CUBE is not involved

</details>

**Q2. Leg A negotiates telephone-event PT 101, leg B PT 96. What feature makes this work, and what breaks without it?**

<details><summary>Answer key</summary>

- ✅ CUBE's asymmetric telephone-event payload-type interworking
- ✅ Symptom without it: two-way audio is fine but key presses are ignored
- ⬜ Force both legs to renegotiate to PT 101
- ⬜ Insert an MTP to normalize the payload type

</details>

**Q3. Which two conditions force an MTP into a DTMF design — and which Cisco document tells you to avoid exactly that?**

<details><summary>Answer key</summary>

- ✅ A leg supports only in-band tones (tone detection needs a DSP)
- ✅ Legs share no common/interworkable method, so UCM inserts an MTP
- ⬜ MTPs are harmless because they are software
- ⬜ Both legs already negotiate RFC 2833

</details>

**Q4. Why does G.729 break in-band DTMF but not RFC 2833?**

<details><summary>Answer key</summary>

- ✅ G.729 is a low-bitrate model-based codec that distorts dual-sine tones
- ✅ RFC 2833 sends the digit as a named event, not audio (codec-independent)
- ⬜ G.711 also breaks in-band DTMF
- ⬜ RFC 2833 fails on G.729 exactly like in-band tones

</details>

## Interactive items for this topic

[MX1](../item-types/matrix/MX1.md)

---
_Source of truth: anchor every answer to the authoritative Cisco document. See the item YAML for source URLs. Part of **CollabForge** — the CCIE Collaboration Design-item bank._