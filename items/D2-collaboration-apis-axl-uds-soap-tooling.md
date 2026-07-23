# D2 · Collaboration APIs: AXL, UDS & SOAP Tooling

> **Blueprint domain:** Domain 1 — Protocols & APIs  ·  **Item type coverage:** scenario Q&A, matrix (MX2)

**After this item you can:**

- Explain what each API family actually does on the wire
- Design bulk provisioning that survives AXL throttling and publisher-only writes
- Prototype and validate API workflows in SoapUI before committing the design

## Concepts & theory

_Read each topic in three passes — the **concept**, the **worked example**, the **exam angle** — then close the page and re-derive the design rule from memory._

### Topic 1 · AXL: how SOAP provisioning really works

AXL is a SOAP web service on UCM (port 8443, /axl/). A client sends an XML envelope describing an operation — addPhone, updateLine, getUser — and UCM executes it directly against its configuration database. The contract is a versioned WSDL/XSD schema shipped per UCM release: AXLAPI.wsdl defines every operation, every field, every type.

- Transport: HTTPS POST of a SOAP envelope; auth = UCM app/end user with Standard AXL API Access role.
- WRITES go to the PUBLISHER only — subscribers can serve reads.
- Schema is versioned: request headers pin it (e.g., 12.5 vs 14.0 schema).
- Response returns the new object's pkid (database UUID) — your handle for updates.

**Worked example.** addPhone envelope (abridged): <ns:addPhone><phone><name>SEP001122334455</name><product>Cisco 8865</product><devicePoolName>HQ-DP</devicePoolName><lines>…DN 3001…</lines></phone></ns:addPhone> → response <return>{pkid}</return>. One HR-feed row becomes one such call; 5,000 hires = 5,000 calls — which is why throttling design (next) matters.

**Exam angle.** Two facts are repeatedly tested: writes are publisher-only, and the schema is per-release. Both are stated constraints in middleware design items.

### Topic 2 · AXL throttling, batching & executeSQLQuery

UCM defends itself: AXL writes are throttled (change notifications, DB write limits), and oversized responses are rejected. A bulk design that fires thousands of writes serially at 9 AM will be throttled or will degrade call processing. Correct design: batch off-hours, pace requests, implement back-off on throttle responses, and use executeSQLQuery (read-only SQL) for bulk reads instead of thousands of get* calls.

- Throttle behavior = HTTP 503/socket pushback; clients MUST implement retry with back-off.
- Schedule bulk writes in maintenance windows; pace (e.g., 1–5 writes/sec sustained).
- executeSQLQuery: direct Informix reads (device, enduser, numplan tables) — fast bulk reads.
- executeSQLUpdate exists but bypasses validation — design reviews should challenge it.

**Worked example.** Requirement: nightly report of all registered phones + descriptions. Wrong design: 30,000 getPhone calls. Right design: ONE executeSQLQuery — 'select name, description from device where tkclass=1' — paged if large. For the HR onboarding feed: queue rows, write 2/sec from 22:00, exponential back-off on 503, resume token for restart.

**Exam angle.** Items contrast a naive serial-write design with a batched/paced one and ask which constraint (throttle, publisher CPU, business hours) the bad design violates.

### Topic 3 · UDS: the user-facing read API behind login

User Data Service is a REST/XML API every UCM node serves (/cucm-uds/). It is how clients FIND their cluster and settings: the Webex App queries UDS to locate the user's home cluster (service discovery), read their devices, lines, and self-care settings. It deliberately exposes user-scope reads and limited self-service writes — it is not an admin provisioning interface.

- Reads work on ANY node — no publisher dependency; scales with the cluster.
- Drives login: _collab-edge SRV → Expressway → UDS user lookup → home cluster.
- ILS-linked clusters answer UDS queries for remote users (intercluster discovery).
- Self-service writes only (e.g., user's own speed dials) — by design.

**Worked example.** GET https://ucm1:8443/cucm-uds/users?username=kashif → XML with the user's home cluster + servers. During MRA login, Expressway-C proxies exactly this query. Design use: a 3-cluster estate with ILS lets one UDS query find any user — which is why the design answer for 'soft clients must log in with only a username' is UDS + ILS, never AXL.

**Exam angle.** 'Which API does the Webex App use to find its home cluster?' — UDS via service discovery. AXL is the distractor.

### Topic 4 · Serviceability XML (SXML): RisPort70 & PerfMon — prototyped in SoapUI

The Serviceability APIs answer 'what is happening right now': RisPort70 returns real-time device registration state (which node, IP, status), PerfmonPort reads performance counters, and CDRonDemand fetches call records. Like AXL they are SOAP services with published WSDLs — which makes SoapUI the standard design-validation tool: import WSDL, set credentials, fire a request, inspect the XML before any code exists.

- RisPort70 selectCmDevice: registration status for up to 1,000 devices per query.
- PerfmonPort: any RTMT counter (calls active, registered phones, CPU) over SOAP.
- SoapUI workflow: import WSDL → auth (HTTPS+basic) → sample request → validate response.
- Poll-interval discipline: dashboards must respect query limits (don't poll 30k devices/5s).

**Worked example.** Design validation for a registration dashboard: in SoapUI, import https://ucm:8443/realtimeservice2/services/RISService70?wsdl, run selectCmDevice with SearchItems=SEP*, confirm the response model (Registered/UnRegistered + node). Then size polling: 30,000 phones ÷ 1,000 per query = 30 queries per sweep; sweep every 60 s, not every 5 s.

**Exam angle.** Match the tool to the phase: SoapUI = design-time validation of SOAP APIs; the DevNet SXML tutorial is the cited workflow.

### Topic 5 · Webex REST API — and choosing the right API per requirement

The Webex REST API is the cloud counterpart: OAuth bearer tokens, JSON, resources like /people, /devices, /telephony/config. Integrations (user-context) and bots (machine-context) are the token models; webhooks push events instead of polling. The design skill this module tests is API SELECTION: map each requirement sentence to AXL, UDS, SXML, or Webex REST — and justify it with one architectural fact.

- Webex REST = Control Hub-managed estate: users, workspaces, devices, calling config, reports.
- OAuth integration for user-context tools; bot token for autonomous services; webhooks for events.
- Hybrid estates usually need TWO APIs: AXL for UCM depth + Webex REST for cloud objects.
- Selection heuristic: WHO owns the object (UCM DB vs cloud) and WHO acts (admin vs user vs machine).

**Worked example.** GET https://webexapis.com/v1/devices with 'Authorization: Bearer <token>' → JSON inventory with connection status — the cloud twin of RisPort70. Mixed requirement: 'provision UCM phones for new hires AND order their cloud workspaces' = AXL (publisher, batched) + Webex REST (devices/workspaces) orchestrated by one middleware, each least-privilege.

**Exam angle.** Requirement-to-API mapping table items: bulk UCM config→AXL; login lookup→UDS; live registration→RisPort70; cloud automation→Webex REST.

## Decide fast — requirement → design answer

| When the brief says… | The design answer is… |
|---|---|
| Bulk provision 5k phones on UCM | AXL — publisher, batched, back-off |
| Client finds home cluster at login | UDS + ILS |
| Live registration dashboard | SXML RisPort70 (paced polling) |
| Bulk read of device table | AXL executeSQLQuery |
| Cloud workspaces / device reports | Webex REST + webhooks |

## Worked design scenario

**The customer ask.** A customer wants HR-driven provisioning (new hires get a phone + line by next morning), a self-service portal for users' own SNR settings, and a NOC wallboard of registration status across 3 ILS-linked clusters.

**The model answer.**

- HR feed → middleware → AXL: publisher-targeted, queued writes 22:00–05:00, 2/sec pace, back-off on 503, pinned schema per cluster version.
- Self-service → UDS self-care writes where supported; otherwise narrow AXL operations behind the portal with a least-privilege app user.
- Wallboard → RisPort70 per cluster, 1,000 devices/query, 60 s sweep; validated first in SoapUI.
- Per-cluster API inventory documented: versions, credentials, roles, throttle policy — that table is the design artifact.

## Check yourself — exam-style questions

_Multiple-answer (select all that apply). Try each in ~2 minutes before revealing the key._

**Q1. Why must the provisioning middleware target the publisher, and what two protections keep it from harming call processing?**

<details><summary>Answer key</summary>

- ✅ AXL writes are serviced only by the publisher (owns the writable DB)
- ✅ Batch/pace writes into maintenance windows
- ✅ Detect AXL throttle (503) and back off exponentially
- ⬜ Spread writes across subscribers for load balancing

</details>

**Q2. Webex App users log in with only a username across 3 clusters. Which API + which replication service make that work?**

<details><summary>Answer key</summary>

- ✅ UDS answers the user lookup
- ✅ ILS links clusters to resolve the user's home cluster
- ⬜ AXL performs the client login
- ⬜ The publisher must be reachable for every user login

</details>

**Q3. A wallboard needs status of 30,000 devices. Which API, what per-query limit, and what polling design follows?**

<details><summary>Answer key</summary>

- ✅ Serviceability XML RisPort70 (selectCmDevice)
- ✅ 1,000 devices per query → 30 queries per sweep
- ⬜ Poll AXL getPhone 30,000 times
- ⬜ AXL returns real-time registration status

</details>

**Q4. Name the token models for Webex REST automation and when each is correct.**

<details><summary>Answer key</summary>

- ✅ Integration (OAuth authorization-code) tokens to act as a user
- ✅ Bot tokens for autonomous machine identities
- ✅ Webhooks so services react to events instead of polling
- ⬜ A personal access token from developer.webex.com in production

</details>

## Interactive items for this topic

[MX2](../item-types/matrix/MX2.md)

---
_Source of truth: anchor every answer to the authoritative Cisco document. See the item YAML for source URLs. Part of **CollabForge** — the CCIE Collaboration Design-item bank._