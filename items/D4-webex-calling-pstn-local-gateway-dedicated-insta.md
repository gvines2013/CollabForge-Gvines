# D4 · Webex Calling: PSTN, Local Gateway, Dedicated Instance & UCM Interconnect

> **Blueprint domain:** Domain 5 — Edge Services  ·  **Item type coverage:** scenario Q&A, matrix (MX3, MX4, MX5, MX6), drag-and-drop (DDG1)

**After this item you can:**

- Recommend Calling Plan vs CCP vs Local Gateway per geography, control and survivability
- Choose the LGW trunk model from capacity and security requirements — with the real numbers
- Position Dedicated Instance honestly, and reproduce the UCM↔Webex dial-plan object chain

## Concepts & theory

_Read each topic in three passes — the **concept**, the **worked example**, the **exam angle** — then close the page and re-derive the design rule from memory._

### Topic 1 · The PSTN triad for Webex Calling

Every Webex Calling design starts with: how do calls reach the PSTN? Three options. Cisco Calling Plan: Cisco is your carrier, numbers ordered in Control Hub — simplest, but country coverage decides. Cloud Connected PSTN (CCP): a certified provider already peered with the Webex cloud — keeps a provider relationship with zero premises equipment. Premises-based (Local Gateway): your SBC connects Webex Calling to existing carrier trunks and/or your PBX — maximum control, required for on-prem interconnect.

- Calling Plan: fastest to deploy; check per-country availability first.
- CCP: provider choice/geo coverage without on-prem hardware.
- LGW: keep contracts & numbers, interconnect UCM/PBX, phased migration.
- Mixed designs are normal: per-location PSTN choice in Control Hub.

**Worked example.** 14-country retailer: 9 countries covered by Calling Plan → use it (no hardware). 3 countries have mandatory local carriers → CCP where those carriers are certified. 2 countries have long PSTN contracts AND a UCM contact center → Local Gateways there, doing double duty: PSTN access + UCM interconnect. One org, three PSTN options, chosen per location.

**Exam angle.** Requirement phrases map directly: 'no on-prem assets' → Calling Plan/CCP; 'keep our carrier' → CCP or LGW; 'connect to UCM' → LGW (only option).

### Topic 2 · Local Gateway trunk models: registration vs certificate

An LGW trunk authenticates to the Webex cloud in one of two ways. Registration-based: the trunk REGISTERs with digest credentials (username/password from Control Hub) — simple, works behind any NAT, but capped at 250 concurrent calls and CUBE-only. Certificate-based: mutual TLS with a CA-signed certificate whose FQDN matches a claimed domain and public DNS — heavier prerequisites, but scales past 250 and supports multi-vendor SBCs and Webex for Government.

- Registration: ≤250 calls (≈2,500 users), CUBE IOS-XE 17.6.1a+, digest auth, dynamic NAT OK.
- Certificate: >250 calls, CUBE 17.9.1a+ / Oracle / AudioCodes / Ribbon / anynode / Italtel.
- Cert rules: CA-signed, NO wildcard, Server-Auth EKU, FQDN in Contact header; domain claim + public DNS A/SRV.
- Cert-based needs public IP or static NAT; reg-based opens pinholes via outbound REGISTER.

**Worked example.** Requirement: 1,800 concurrent PSTN calls through one LGW over the Internet. 1,800 > 250 → certificate-based, full stop. Prerequisites to write into the design: claim example.com in Control Hub, publish lgw1.example.com in public DNS, buy a CA-signed cert (SAN = lgw1.example.com, no wildcard), static NAT, IOS-XE ≥ 17.9.1a. Each missed prerequisite is a Design-module distractor option.

**Exam angle.** The 250-call line is the discriminator. Also: Webex for Government = certificate-based + CUBE only.

### Topic 3 · Capacity & connectivity: OTT vs Edge Connect, media PoPs

How the LGW reaches the cloud sets its ceiling. Over-the-top Internet: fine to ~2,000 sessions per LGW with link quality of ≤100 ms one-way, ≤10 ms jitter, ≤0.5% loss. Webex Edge Connect: dedicated private peering into the Webex backbone — SLA-grade, scales one LGW toward ~6,500 sessions. Every LGW is provisioned against TWO geographically separated Webex media PoPs via DNS SRV for redundancy; firewalls must allow both.

- ≤250 sessions: reg-based OTT. 250–2,000: cert-based OTT. >2,000 or SLA: cert + Edge Connect.
- Two media PoPs per LGW (SRV-driven) — allow both in firewall/routing design.
- Regional media: calls keep media in-region where possible.
- Quality targets are contractual design inputs, not aspirations: 100/10/0.5.

**Worked example.** Sizing walk: HQ needs 2,400 concurrent sessions. OTT tops out ~2,000 → either two cert-based LGWs behind a route group (1,200 each, N+1 math) or one LGW on Edge Connect. The design answer weighs cost (circuit) vs operational simplicity (one box) — and either way documents both media PoP destinations and the 100/10/0.5 link targets.

**Exam angle.** Numbers to recall cold: 250 / ~2,000 OTT / ~6,500 Interconnect, and 100 ms / 10 ms / 0.5%.

### Topic 4 · Dedicated Instance: what it is, what it isn't

Dedicated Instance (DI) is Cisco-operated UCM, IM&P (optional), Unity Connection, Expressway (MRA + B2B), CER in the Americas, and optionally SME — hosted in Webex data centers, integrated with Webex Calling, sold as an add-on. It is THE migration answer when full UCM features, older endpoints, or deep customization make multi-tenant Webex Calling impossible. It is NOT 'Webex Calling with extra features' — the two platforms' features are not harmonized.

- Sizing: up to 8 call-processing nodes ≈ 50,000 devices/cluster; 160,000 max end users.
- MRA entitlement = 100% of Knowledge Workers (20% deployed at activation, expand by case); B2B = 5% KW.
- SME eligibility at 3+ DI clusters — centralizes trunks/routing across clusters.
- Nightly DRS backups, last 3 kept, disaster-recovery only — not a rollback tool.
- Cross-platform gap example: a Webex Calling user cannot join a DI hunt group.

**Worked example.** Customer demands 'all UCM features in the cloud' for 30,000 devices including 7900-series phones and CTI integrations. DI fits: one cluster (≤50k devices), MRA for remote staff within the 100% KW entitlement, Unity + IM&P included. The honest caveats in the design: split users across DI and multi-tenant WxC will see non-harmonized features, and backups are DR-only — change control still matters.

**Exam angle.** Items test the sizing facts and the harmonization caveat — 'can the WxC receptionist cover DI users' hunt group?' No.

### Topic 5 · The UCM ↔ Webex Calling interconnect object chain

When UCM and Webex Calling coexist, Cisco's reference design is a fixed chain of UCM objects — and the Design module loves asking for their order. Differentiation trick first: if the LGW and PSTN gateway are the same CUBE, UCM must tell Webex traffic from PSTN traffic → two trunks on different ports. Then the chain routes UCM→Webex calls and normalizes abbreviated dialing.

- 1) SIP Trunk Security Profile, dedicated port (e.g., 5065 for Webex traffic).
- 2) SIP Profile with OPTIONS ping  3) Webex CSS = DN + ESN + PSTN + onNetRemote partitions.
- 4) SIP trunk (run-on-all-nodes, AAR CSS for PSTN reroute) → 5) Route Group → 6) Route List.
- 7) Webex partition → 8) urgent +E.164 route patterns per Webex DID range → 9) urgent ESN translation patterns (+E.164 mask, originator's CSS, no interdigit wait).

**Worked example.** Webex location owns +1 408 555 01XX, ESN 8012 1XX. UCM objects: route pattern \+140855501XX (partition Webex, RL_Webex, urgent) and translation 80121XX → mask +140855501XX (urgent, originator's CSS, no interdigit wait). Inbound from Webex lands in the Webex CSS, which sees DN/ESN/PSTN/onNetRemote — so a Webex user can dial a UCM DN, an ESN, or break out to PSTN. onNetRemote matters only when ILS/GDPR is in play.

**Exam angle.** Drag-and-drop ordering of this exact chain is a known item style; the 'two trunks, two ports' rationale is the free-text trap.

## Decide fast — requirement → design answer

| When the brief says… | The design answer is… |
|---|---|
| No on-prem assets, covered country | Cisco Calling Plan |
| 1,800 concurrent calls, one LGW | Certificate-based trunk |
| Keep carrier contracts, no SBC | Cloud Connected PSTN |
| Full UCM features in cloud | Dedicated Instance |
| >2,000 sessions or SLA mandate | Webex Edge Connect |

## Worked design scenario

**The customer ask.** Global retailer: 300 small sites in 14 countries, 2 HQs with UCM-based contact centers, long PSTN contracts in 2 countries, cloud calling target in 18 months, board demands per-site survivability for the top 20 stores.

**The model answer.**

- Sites → multi-tenant Webex Calling; PSTN per location: Calling Plan where covered, CCP for mandated carriers.
- HQs → certificate-based LGW pairs: PSTN for contract countries + UCM interconnect (two trunks, distinct ports).
- UCM↔Webex object chain with urgent +E.164 patterns and ESN normalization; onNetRemote included (ILS in play).
- Top-20 stores → Webex Calling Survivability Gateway; DI rejected: no full-UCM-feature requirement at sites.
- Capacity check per HQ LGW against 2,000 OTT ceiling; Edge Connect priced as the alternative.

## Check yourself — exam-style questions

_Multiple-answer (select all that apply). Try each in ~2 minutes before revealing the key._

**Q1. A design needs 1,800 concurrent calls via one Internet-connected LGW. Trunk model, and the four prerequisites it imposes?**

<details><summary>Answer key</summary>

- ✅ Certificate-based trunk (1,800 > 250 and ≤ ~2,000 OTT)
- ✅ Domain claimed/verified with the LGW FQDN in public DNS
- ✅ CA-signed certificate (no wildcard, Server-Authentication EKU)
- ⬜ Registration-based because it is easier behind NAT

</details>

**Q2. Which PSTN option connects Webex Calling to an existing UCM — and why are the other two structurally unable to?**

<details><summary>Answer key</summary>

- ✅ Premises-based PSTN via Local Gateway
- ✅ Calling Plan and CCP terminate to the carrier, not to on-prem UCM
- ⬜ Cisco Calling Plan connects directly to the existing UCM
- ⬜ Cloud Connected PSTN registers to the on-prem UCM

</details>

**Q3. Order the nine UCM objects for routing +E.164 and ESN calls to Webex Calling.**

<details><summary>Answer key</summary>

- ✅ A SIP Trunk Security Profile on a dedicated port (e.g., 5065)
- ✅ A SIP Profile with OPTIONS ping keepalive
- ✅ Partitions/CSS steering +E.164 and ESN to the Webex trunk
- ⬜ Reusing the default 5060 profile because one trunk already works

</details>

**Q4. A customer plans 60,000 devices on one DI cluster with WxC users in DI hunt groups. Name both design errors.**

<details><summary>Answer key</summary>

- ✅ Capacity: a DI cluster ≈ 50,000 devices, so 60,000 needs a second cluster
- ✅ Placing Webex Calling (multi-tenant) users in DI (UCM) hunt groups mixes platforms
- ⬜ 60,000 devices fit comfortably on one DI cluster
- ⬜ DI and Webex Calling multi-tenant share the same hunt-group object

</details>

## Interactive items for this topic

[MX3](../item-types/matrix/MX3.md), [MX4](../item-types/matrix/MX4.md), [MX5](../item-types/matrix/MX5.md), [MX6](../item-types/matrix/MX6.md), [DDG1](../item-types/drag-and-drop/DDG1.md)

---
_Source of truth: anchor every answer to the authoritative Cisco document. See the item YAML for source URLs. Part of **CollabForge** — the CCIE Collaboration Design-item bank._