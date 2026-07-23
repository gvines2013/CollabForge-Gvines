# D7 · Edge: CUBE Multi-Tenancy, IPsec, Video Mesh & Expressway Clustering

> **Blueprint domain:** Domain 5 — Edge Services  ·  **Item type coverage:** scenario Q&A, matrix (MX6), drag-and-drop (DD2)

**After this item you can:**

- Design multi-tenant CUBE edges with real isolation, not just separate dial-peers
- Place IPsec only where TLS/SRTP can't satisfy the mandate — and pay its QoS bill
- Size Video Mesh and Expressway clusters with the rules that exam items quote

## Concepts & theory

_Read each topic in three passes — the **concept**, the **worked example**, the **exam angle** — then close the page and re-derive the design rule from memory._

### Topic 1 · CUBE multi-tenancy: voice class tenant

One physical CUBE can present itself as several logically separate SBCs. A 'voice class tenant' bundles per-trunk SIP identity: bound interfaces/addresses, registrar and credentials, SIP profiles, timers, even listen ports. Dial-peers reference a tenant and inherit its personality. Use cases: one edge serving multiple business units, multiple ITSPs with contradictory SIP requirements, or a provider hosting many customers on shared hardware.

- Tenant = per-trunk config container; dial-peers inherit via 'voice-class sip tenant <n>'.
- Conflicting ITSP quirks (different From-header rules, timers) live in different tenants.
- Per-tenant max-conn caps one customer's blast radius.
- Tenants separate SIP personality — NOT IP routing. That's the next topic.

**Worked example.** Tenant sketch: voice class tenant 100 → registrar reg1.itsp-a.com, credentials user A, sip-profile 100 (PAI rewrite), bind Gi0/0/1. Tenant 200 → certificate-based Webex LGW personality, bind Gi0/0/2, its own listen port. Dial-peer 1001 'voice-class sip tenant 100'; dial-peer 2001 tenant 200. Two SBCs to the outside world, one chassis to operate.

**Exam angle.** 'Two providers demand contradictory SIP behavior on one CUBE' → tenants, each with its own SIP profile set.

### Topic 2 · Multi-VRF + per-tenant CAC: real isolation

Tenants separate SIP identity; VRFs separate the network. VRF-aware CUBE puts each customer/BU into its own routing table — overlapping IP space (every customer is 10.0.0.0/8), no cross-talk, separate media binds. The complete multi-tenant design stacks three layers: tenant (SIP), VRF (L3), and per-tenant CAC (capacity), so one tenant's robocall storm can't eat another's trunk.

- VRF-aware routing: per-VRF dial-peer/binds; media stays inside the customer VRF.
- Overlapping address space across customers becomes a non-issue.
- Per-tenant max-conn + call spike = capacity blast-radius control.
- MSP design = tenant + VRF + CAC stated together; any one alone is incomplete.

**Worked example.** MSP hosts companies A, B, C on a C8300 pair. A and B both use 10.1.0.0/16 internally — fine: VRF-A and VRF-B each bind their own sub-interface and media address. Tenant per company carries its SIP credentials. max-conn 80/60/40 per tenant matches each contract. Exam-style probe: 'customer B's burst takes down A's calls — what was missing?' Per-tenant CAC.

**Exam angle.** Know what each layer isolates: tenant=SIP, VRF=routing/media, CAC=capacity. Items remove one and ask the consequence.

### Topic 3 · IPsec placement: when TLS/SRTP isn't enough

Calls already encrypt natively: TLS for signaling, SRTP for media — per-call, end-to-end-ish, the PA default. IPsec (IKEv2 site-to-site, or GETVPN for any-to-any WAN) earns a place only when native call security can't satisfy the mandate: legacy gear that can't do TLS/SRTP, 'ALL traffic must be encrypted in transit' compliance wording (covers signaling, media, AND management), or untrusted transport carrying mixed cleartext. The design bill: IPsec adds ~50–60 bytes per packet, which inflates LLQ math.

- Default answer: TLS/SRTP per call — name it before reaching for IPsec.
- IPsec wraps segments, not calls: tunnel the legacy/cleartext stretch only.
- QoS: voice packet ~200 B grows ~25–30% — resize the LLQ; qos pre-classify preserves DSCP-based queuing on the tunnel.
- GETVPN keeps any-to-any WAN QoS/routing intact (no tunnel hub) for big private WANs.

**Worked example.** LLQ math with IPsec: 10 G.711 calls × 80 kb/s = 800 kb/s native. Wrapped in IPsec: ≈ 10 × 104 kb/s ≈ 1,040 kb/s — the 1,000 kb/s LLQ that looked generous is now undersized. Exam exhibit shows exactly this: voice fine before encryption project, choppy after. Answer: re-size LLQ for IPsec overhead + qos pre-classify.

**Exam angle.** Two tested facts: IPsec is the exception not the default, and its overhead breaks previously correct LLQ sizing.

### Topic 4 · Video Mesh: local media with cloud cascade

Video Mesh nodes are on-prem media servers for Webex meetings. Apps and devices send media to the nearest healthy node cluster instead of the cloud — slashing Internet bandwidth and latency. When someone external (or overflow beyond node capacity) joins, the node builds ONE cascade link to the cloud carrying the shared streams. The golden rule: capacity exhaustion NEVER blocks a join — media simply overflows to the cloud. The cascade link is the design's pinch point: size it, mark it, monitor it.

- Placement: per campus/region where meeting density justifies nodes.
- Overflow → cloud, always; Mesh is an optimization, not a gate.
- Cascade = one aggregated link per meeting spanning premises+cloud; mark AF41-class.
- Nodes need outbound HTTPS + media reachability; health/metrics in Control Hub.

**Worked example.** HQ, 4,000 staff, heavy internal meetings: 2-node cluster (n+1 for maintenance). Internal-only meeting: all media stays on-net — Internet usage ≈ 0. Customer joins from outside: cascade forms; instead of 30 staff each streaming to cloud (30× bandwidth), ONE cascade carries the meeting. Bandwidth answer in the design: cascade sized for concurrent cascaded meetings × per-meeting rate, marked and queued like interactive video.

**Exam angle.** 'Node cluster at capacity — what does the next participant experience?' Joins via cloud. Anyone answering 'busy' fails the item.

### Topic 5 · Expressway clustering: the rules that get tested

Expressway clusters scale and protect MRA, B2B, and traversal. The rules are crisp and exam-quotable: up to 6 peers per cluster; peer 1 is the configuration master (config replicates outward — edit on the master); peers need the SAME software version and <80 ms round-trip between them; certificates must carry the cluster FQDN AND each peer FQDN in SANs; DNS SRV records spread client load across peers. Pattern: clustered C inside + clustered E in the DMZ, traversal zones from every C peer to every E peer.

- 6 peers max; master-based config replication (never edit non-masters).
- <80 ms RTT between peers — geo-split clusters must respect it.
- Cert SANs: cluster FQDN + all peer FQDNs (+ domains for MRA).
- _collab-edge._tls SRV per E peer with equal priority/weight = client load distribution.

**Worked example.** Growing MRA from 2,500 to 7,000 sessions: 3-peer E cluster (and matching C). Checklist that IS the exam answer: same X-version on all peers, RTT 12 ms (OK), new cert with SANs expc-cluster.corp.com + expe1/2/3.corp.com + collab-edge domain, SRV records for all three E peers, traversal zones full-mesh C→E. Miss the SAN update and TLS fails cluster-wide — the classic post-expansion incident.

**Exam angle.** Memorize: 6 / master / <80 ms / same version / SAN list / SRV spread. Items quiz exactly these six.

## Decide fast — requirement → design answer

| When the brief says… | The design answer is… |
|---|---|
| Two ITSPs, contradictory SIP rules | voice class tenants |
| Customers with overlapping IP space | Multi-VRF CUBE |
| 'Encrypt ALL transport' mandate | IPsec wrap + LLQ resize |
| Keep meeting media on-net | Video Mesh cluster |
| MRA scale + resilience | Expressway cluster (6 rules) |

## Worked design scenario

**The customer ask.** An MSP hosts voice edges for three acquired companies (overlapping 10.x space) on shared C8300s. One company is under an 'all transport encrypted' regulation. The 4,000-person HQ wants meeting media kept on-net, and MRA must grow from 2,500 to 7,000 sessions.

**The model answer.**

- CUBE pair: three tenants (SIP personality per company) + three VRFs (overlapping IP, media isolation) + per-tenant max-conn/call-spike.
- Regulated company: IKEv2 IPsec wrap on its transport; LLQ re-sized ~+30%; qos pre-classify on tunnels.
- HQ: 2-node Video Mesh cluster (n+1); cascade link sized, AF41-marked, monitored in Control Hub.
- Expressway: 3-peer C and E clusters — same version, <80 ms, cluster+peer FQDN SANs, SRV across E peers, full-mesh traversal zones.
- Per-layer failure behavior documented: tenant CAC rejection, VRF separation test, Mesh overflow to cloud.

## Check yourself — exam-style questions

_Multiple-answer (select all that apply). Try each in ~2 minutes before revealing the key._

**Q1. What does a voice class tenant isolate, and which TWO additional layers complete customer isolation?**

<details><summary>Answer key</summary>

- ✅ A tenant isolates SIP personality per trunk (bindings, credentials, profiles, ports)
- ✅ VRFs add network-path isolation
- ✅ Per-tenant normalization/credentials complete the isolation
- ⬜ VRFs alone are sufficient for full customer isolation

</details>

**Q2. Voice was fine until the IPsec project; now it's choppy at peak. Explain with numbers and name the two fixes.**

<details><summary>Answer key</summary>

- ✅ IPsec adds ~50–60 bytes/packet, raising a G.711 call to ~104 kb/s
- ✅ Re-provision CAC/QoS bandwidth to include the IPsec overhead
- ✅ Reduce overhead with compression / larger payloads (fewer pps)
- ⬜ IPsec adds no measurable overhead to voice

</details>

**Q3. A Video Mesh cluster is at capacity when the CEO joins. What happens, and why must the design state it?**

<details><summary>Answer key</summary>

- ✅ The CEO joins normally — overflow participants use cloud media
- ✅ Video Mesh never blocks a join (overflow architecture)
- ✅ The design must explicitly state the overflow behaviour
- ⬜ The join fails or the CEO hears busy

</details>

**Q4. List the six Expressway clustering rules an expansion from 1 to 3 peers must satisfy.**

<details><summary>Answer key</summary>

- ✅ Maximum 6 peers per cluster
- ✅ All peers on the same software version
- ✅ <80 ms round-trip delay between any two peers
- ⬜ Peers may run mixed software versions in steady state

</details>

## Interactive items for this topic

[MX6](../item-types/matrix/MX6.md), [DD2](../item-types/drag-and-drop/DD2.md)

---
_Source of truth: anchor every answer to the authoritative Cisco document. See the item YAML for source URLs. Part of **CollabForge** — the CCIE Collaboration Design-item bank._