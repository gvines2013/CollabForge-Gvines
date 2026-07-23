# D14 · Media Resources & Meeting Security Design

> **Blueprint domain:** Domain 6 — Media Resources & Meetings  ·  **Item type coverage:** scenario Q&A

**After this item you can:**

- Place transcoders, MTPs, MoH and conference bridges where they are actually needed.
- Choose IOS-XE ad-hoc conferencing vs Cisco Meeting Server by scale and feature.
- Design secure meetings: roles, PMR security and end-to-end encryption plus identity.
- Avoid unplanned media-resource insertion that degrades a design.

## Concepts & theory

_Read each topic in three passes — the **concept**, the **worked example**, the **exam angle** — then close the page and re-derive the design rule from memory._

### Topic 1 · Media resources: transcoding, MTP, MoH, annunciator

Media resources are DSP/software services UCM invokes via Media Resource Groups (MRG) and Lists (MRGL). Transcoders convert between codecs; MTPs bridge capabilities (DTMF, early offer); MoH streams hold audio; the annunciator plays tones/announcements.

- MRGL on device pool / device controls which resources a call can use and enforces locality.
- Transcoder needed only when no common codec exists; MTP only to bridge a capability gap.
- MoH source (multicast vs unicast) and codec affect WAN bandwidth — design per site.

**Worked example.** WAN saturates during hold because unicast G.711 MoH streamed from HQ. Multicast MoH from a branch source (or G.729 MoH) cuts the WAN load dramatically.

**Exam angle.** MoH bandwidth and resource locality are controlled by MRGL design, not by the codec alone.

### Topic 2 · Ad-hoc & meet-me conferencing on IOS-XE

Small ad-hoc conferences can use IOS-XE DSP-based conference bridges registered to UCM. They are simple and local but limited in size and features compared with a dedicated conferencing platform.

- IOS-XE conference bridges suit branch ad-hoc/meet-me with modest party counts.
- DSP sizing (PVDM) bounds simultaneous conferences and transcoding together.
- Beyond small scale or for rich meetings, move to Cisco Meeting Server.

**Worked example.** Branch ad-hoc conferences fail at peak. PVDM DSP was shared between transcoding and conferencing and ran out; re-sizing DSP farms (or offloading to CMS) resolves contention.

**Exam angle.** Conference-resource exhaustion items hinge on shared DSP (PVDM) sizing.

### Topic 3 · Cisco Meeting Server for scalable meetings

CMS provides scalable, interoperable conferencing (spaces, SIP/Lync interop, recording, large meetings) and integrates with UCM and Webex. It scales via clustering/load balancing and supports rich layouts and guest access.

- CMS spaces + call bridge groups scale conferencing beyond IOS-XE limits.
- Standards-based SIP interop bridges third-party and Microsoft endpoints.
- iX/ActiveControl carries roster/layout control with UCM endpoints.

**Worked example.** An org needs 200-party interoperable meetings with recording. CMS call bridge group provides the scale and SIP interop that IOS-XE bridges cannot, integrated with UCM dial plan.

**Exam angle.** Scale + interop + recording requirements select CMS over IOS-XE conferencing.

### Topic 4 · Webex meetings: scheduling, features, media path

Webex meetings are scheduled via the app/Control Hub and can keep media on-prem with Video Mesh when participants are internal, overflowing to the cloud when capacity or external participants require it.

- Video Mesh keeps internal media local (bandwidth savings) and never blocks — overflow to cloud.
- Scheduling, recording and features are governed in Control Hub by license/role.
- Quality troubleshooting uses Control Hub analytics (the media metrics behind RTCP).

**Worked example.** Internal all-hands hairpins media to the cloud and wastes WAN. Sizing Video Mesh cascade capacity keeps internal participants on-prem with cloud overflow as a safety valve.

**Exam angle.** Video Mesh capacity vs cloud overflow is the on-prem-media design lever for Webex meetings.

### Topic 5 · Meeting security: roles, PMR and E2EE + identity

Secure meetings combine role design (host/cohost/presenter/attendee), Personal Meeting Room hardening (lobby, unlock policy), and end-to-end encryption plus verified identity so only intended participants decrypt media.

- PMR risk: a static personal room can be reused — enforce lobby/registration and auto-lock.
- E2EE plus identity ensures the cloud cannot read media and participants are verified, at the cost of some interop features.
- Participant roles bound who can share, record, admit and mute.

**Worked example.** Sensitive board meetings need provable confidentiality. Use E2EE with identity verification and a locked PMR with explicit admission, accepting the feature trade-offs E2EE imposes.

**Exam angle.** When the ask is 'cloud must not be able to read media + verified participants', that is E2EE plus identity, not just TLS.

## Decide fast — requirement → design answer

| When the brief says… | The design answer is… |
|---|---|
| Hold music saturates WAN | Multicast / low-bitrate MoH via MRGL |
| No common codec on a call | Transcoder (only then) |
| 200-party interoperable meeting | Cisco Meeting Server |
| Keep internal meeting media on-prem | Video Mesh + cloud overflow |
| Cloud must not read media | E2EE plus identity, locked PMR |

## Worked design scenario

**The customer ask.** An enterprise sees WAN saturation on hold and during all-hands, branch ad-hoc conferences failing at peak, and a board demanding provably confidential meetings. Design the media-resource and meeting-security architecture.

**The model answer.**

- Use MRGL to localize resources, multicast/low-bitrate MoH to cut WAN, and reserve transcoders/MTPs only for genuine capability/codec gaps.
- Right-size branch DSP (PVDM) or offload conferencing to Cisco Meeting Server for scale and interop.
- Size Video Mesh cascade capacity so internal all-hands media stays on-prem with cloud overflow.
- For the board, deploy E2EE plus identity with a locked PMR and explicit roles, documenting the interop trade-offs.

## Check yourself — exam-style questions

_Multiple-answer (select all that apply). Try each in ~2 minutes before revealing the key._

**Q1. Hold music is saturating the WAN between HQ and branches. Which design levers fix it and which UCM construct enforces them?**

<details><summary>Answer key</summary>

- ✅ Switch MoH to multicast / a low-bitrate codec
- ✅ Source MoH locally at each site
- ✅ MRGL enforces resource locality
- ⬜ Simply increase the WAN bandwidth

</details>

**Q2. A customer needs 200-party meetings with third-party interop and recording. Why not IOS-XE ad-hoc conferencing, and what do you choose?**

<details><summary>Answer key</summary>

- ✅ Cisco Meeting Server (call bridge groups) for scale + interop + recording
- ✅ CMS provides standards-based SIP interop and recording
- ⬜ IOS-XE conference bridges scale to 200 interoperable parties
- ⬜ Stack more PVDM DSP into the routers

</details>

**Q3. A board requires meetings the cloud provider cannot decrypt, with verified participants. Which Webex capability meets this and what is the trade-off?**

<details><summary>Answer key</summary>

- ✅ End-to-end encryption plus identity
- ✅ Media keys are held only by the participants, not the cloud
- ✅ Trade-off: some interop / features are unavailable
- ⬜ Standard TLS is sufficient because 'meetings are encrypted'

</details>

**Q4. Internal all-hands media is hairpinning through the Webex cloud and wasting WAN. What keeps it on-prem and why does it never block calls?**

<details><summary>Answer key</summary>

- ✅ Cisco Video Mesh keeps internal media on-prem
- ✅ Overflow to the cloud when nodes are full — it never blocks
- ✅ Capacity planning trades WAN savings against node sizing
- ⬜ Disable cloud fallback to force all media on-prem

</details>

---
_Source of truth: anchor every answer to the authoritative Cisco document. See the item YAML for source URLs. Part of **CollabForge** — the CCIE Collaboration Design-item bank._