# D8 · Contact Center: WxCC, Digital Channels & UCCX Positioning

> **Blueprint domain:** Domain 7 — Collaboration Apps & Services  ·  **Item type coverage:** scenario Q&A

**After this item you can:**

- Position GCM queues vs UCCX vs Webex Contact Center from requirement keywords
- Explain the WxCC object model — entry point to agent — and design with it
- Design digital channels through Webex Connect, including blended-agent profiles

## Concepts & theory

_Read each topic in three passes — the **concept**, the **worked example**, the **exam angle** — then close the page and re-derive the design rule from memory._

### Topic 1 · Positioning: three platforms, one decision

Three legitimate 'route calls to a team' answers, separated by capability ceilings. GCM call queues (in Webex Calling): voice-only distribution with light supervision — no flows, no CRM. UCCX: on-premises ACD/IVR bound to UCM — scripted IVR, skills, recording integrations; right where an on-prem mandate or existing UCCX investment rules. Webex Contact Center: cloud-native omnichannel (voice + chat + email + SMS + social), Flow Designer logic, CRM connectors, AI/self-service, elastic seasonal scale, WFO.

- Disqualifier keywords for GCM: omnichannel, CRM screen-pop, IVR logic, skills at scale, WFO.
- UCCX keepers: on-prem mandate, UCM-registered agents, existing script estate.
- WxCC keywords: elastic scale, digital channels, AI agents, analytics depth, cloud-first.
- Migrations run platforms in parallel — waves by queue/line of business.

**Worked example.** Parse this ask: 'agents handle calls AND WhatsApp, Salesforce pop on answer, triple headcount every December'. Three hits — omnichannel, CRM, elastic — each individually disqualifies GCM and strains UCCX. Answer: WxCC, with the dismissals written out. Counter-ask: 'internal IT helpdesk, 12 agents, voice only, lead listens in' → GCM queue + supervisor; WxCC would be over-design.

**Exam angle.** Score comes from the dismissal sentences as much as the selection — name WHY each runner-up fails.

### Topic 2 · The WxCC object model: entry point → queue → team → agent

WxCC routing is a chain of objects. Entry point: the addressable front door per channel (a dialed number, a chat widget, an email address) — it owns the flow that treats the contact. Queue: where contacts wait, with skill and precedence rules. Teams (grouped under sites) hold agents. Agents get a desktop profile (what the desktop shows/permits) and a multimedia profile (how many contacts of which channels they can hold at once). Flows decide everything between entry and queue.

- Entry point per channel — one phone number, one chat widget, one mail address each.
- Queue: skills-based + precedence routing; spill targets between teams.
- Desktop profile = UI/permissions; multimedia profile = concurrent-contact policy.
- Map org language to objects: 'department'→queue+team, 'hotline'→entry point.

**Worked example.** Insurance claims design: entry point 'Claims-Voice' (number) and 'Claims-Chat' (widget) → both flows end in queue 'Claims' (skill: claims-certified) → teams 'Claims-EU' and 'Claims-US' (sites) → 80 agents, desktop profile with Salesforce pane, multimedia profile '1 voice OR 3 chats'. One picture, every object named — that diagram is the design deliverable.

**Exam angle.** Items give a org chart + requirements and ask which objects map where; know each object's single responsibility.

### Topic 3 · Flow Designer: where the logic lives

Every entry point runs a flow — a visual graph that treats the contact before and during queueing: menus and prompts, data dips via HTTP nodes to CRMs/APIs, business-hours branching, queue selection by collected data, queued-contact treatment (announcements, estimated wait, callback offer), and post-call surveys. The design question is always placement: which logic belongs in the flow, which in the CRM, and which in an external service the flow calls.

- Flow nodes: play/collect, condition, HTTP request, set variable, queue contact, callback.
- Data dips: lookup caller in CRM by ANI → branch on customer tier.
- Queued treatment lives in the flow too — position, comfort, callback offer.
- Keep flows thin: complex business rules belong behind an API the flow calls.

**Worked example.** Gold-customer routing: flow does HTTP dip to Salesforce with ANI → response tier='gold' → queue contact to 'Priority' queue with precedence 10; else standard queue. Wait >3 min → callback node offers return call. The same requirement in UCCX would be a CCX script — the exam may show both and ask for the WxCC equivalent object (flow + HTTP node).

**Exam angle.** 'Where does the tier lookup live?' — flow HTTP node calling the CRM; not the agent desktop, not the queue.

### Topic 4 · Digital channels via Webex Connect

Digital channels — email, live chat, SMS, WhatsApp/social — are delivered through Webex Connect (the CPaaS layer). Per channel you create an ASSET in Webex Connect (a chat app, an email app with verified mail domain, an SMS number, a WhatsApp business app registration), then bind that asset to a WxCC entry point. From there, digital contacts flow through the same queue/team/agent model as voice. Each channel has its own onboarding prerequisites — those prerequisites are exam material.

- Asset per channel in Webex Connect → bound to a WxCC entry point.
- Prereqs differ: mail domain verification (email), number provisioning (SMS), Meta business verification (WhatsApp).
- Conversations route via the SAME queues/teams — one routing model.
- Volumes per channel size agent counts and multimedia profiles.

**Worked example.** Adding WhatsApp: register the WhatsApp Business app as an asset in Webex Connect (Meta business verification — lead time!), bind asset → entry point 'Support-WhatsApp', flow routes to queue 'Digital-Support', agents with multimedia profile allowing 3 concurrent messaging contacts. The design's hidden dependency: Meta verification time — call it out, it's the kind of constraint Design items reward.

**Exam angle.** Know the pipeline order: Connect asset → entry point → flow → queue. Items scramble it.

### Topic 5 · Licensing, blended agents & migration design

Agent licensing: standard covers voice-centric work; premium adds digital channels, supervisor capabilities, and richer features — so any omnichannel or supervised design must place premium licenses correctly. Blended agents are governed by the multimedia profile: how many simultaneous contacts per channel (e.g., 1 voice OR 3 chats — voice usually exclusive). Migration design from UCCX: run in waves by queue, keep UCM as the PSTN/telephony estate where needed, and define the cutover metric per wave.

- Premium = digital channels + supervisor; standard = voice agent.
- Multimedia profile is a POLICY object: set it from workload studies, not vibes.
- Supervisors: monitor/coach across channels; dashboards + recordings per policy.
- Wave migration: queue-by-queue, parallel run, rollback criteria stated.

**Worked example.** 120 UCCX agents → WxCC with chat+WhatsApp: 90 standard (voice waves 1–2), 30 premium (digital + 6 supervisors). Multimedia: voice exclusive; messaging cap 3 (from a 2-week workload study). Waves: helpdesk queue first (lowest risk), claims last; success metric per wave = answer SLA parity for 2 weeks; rollback = repoint the entry-point number to UCCX. Every element traces to a requirement or a risk.

**Exam angle.** License-feasibility and profile math are the gotchas: digital work on standard licenses, or 'voice + 2 chats simultaneously' against a voice-exclusive profile.

## Decide fast — requirement → design answer

| When the brief says… | The design answer is… |
|---|---|
| Omnichannel + CRM + elastic | Webex Contact Center |
| On-prem mandate, UCM agents | UCCX |
| Voice team + lead monitoring only | GCM queue + supervisor |
| WhatsApp / chat entry | Webex Connect asset → entry point |
| Voice + concurrent chats per agent | Multimedia profile + premium license |

## Worked design scenario

**The customer ask.** An insurer runs UCCX with 120 agents on UCM. Requirements: add web chat and WhatsApp, Salesforce screen-pop, seasonal scale to 300 agents, supervisors with cross-channel monitoring, and no big-bang cutover.

**The model answer.**

- Platform: WxCC — omnichannel, CRM, elastic scale each disqualify GCM; UCCX fails omnichannel/elastic. Dismissals written out.
- Objects: voice + chat + WhatsApp entry points → flows (Salesforce HTTP dip for screen-pop) → skill queues → site-based teams.
- Digital: Webex Connect assets per channel (Meta verification lead time flagged); same queues route all channels.
- Licensing: premium for digital agents + 6 supervisors; multimedia profile 1-voice-or-3-chats from workload study.
- Migration: queue-by-queue waves off UCCX, parallel run, SLA-parity exit criteria, entry-point repoint as rollback.

## Check yourself — exam-style questions

_Multiple-answer (select all that apply). Try each in ~2 minutes before revealing the key._

**Q1. 'Agents handle voice and two chats; supervisors monitor across channels.' Which platform, and which two objects/licenses implement it?**

<details><summary>Answer key</summary>

- ✅ Webex Contact Center
- ✅ A multimedia profile defining concurrent-contact policy
- ✅ Appropriate agent / premium licences
- ⬜ A GCM queue with a voice-only supervisor

</details>

**Q2. Where are WhatsApp assets created, and what is the four-step pipeline to an agent?**

<details><summary>Answer key</summary>

- ✅ Assets are created in Webex Connect (the CPaaS layer)
- ✅ The WhatsApp Business registration requires Meta business verification
- ✅ Pipeline: asset → flow → queue → agent
- ⬜ The channel is created directly inside WxCC

</details>

**Q3. Name three requirement keywords that individually disqualify GCM queues in favor of a contact center platform.**

<details><summary>Answer key</summary>

- ✅ Omnichannel / digital channels (chat, email, SMS, social)
- ✅ CRM integration / screen-pop
- ✅ IVR flow logic (data dips, menus)
- ⬜ A simple internal voice-only queue

</details>

**Q4. Where should a customer-tier lookup live in WxCC, and which node type performs it?**

<details><summary>Answer key</summary>

- ✅ In the entry point's Flow
- ✅ Performed by an HTTP request node calling the CRM with the ANI
- ⬜ In the agent desktop after the call is answered
- ⬜ Hard-coded statically in the queue

</details>

---
_Source of truth: anchor every answer to the authoritative Cisco document. See the item YAML for source URLs. Part of **CollabForge** — the CCIE Collaboration Design-item bank._