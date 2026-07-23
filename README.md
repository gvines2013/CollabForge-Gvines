# CollabForge — the CCIE Collaboration Design-item bank

**Decode the exam blueprint into design-grade practice.**  CollabForge turns every CCIE
Collaboration **Design module** blueprint topic into practice you can study, self-test, and
extend — built on one repeatable pipeline and anchored to authoritative Cisco documentation.

> This repo is the companion to the blog *“You can prepare the Design module. Here’s the method.”*
> It proves the method scales: **15 design items (D1–D15) covering all seven blueprint domains**,
> **60 scenario questions**, **6 matrix items**, and **4 drag-and-drop items** — every answer source-anchored.

---

## Why the Design module is different

There’s no device to log into and no `show` command to confirm you guessed right — and the answer
is written down nowhere. Design rewards **judgment**: justifying *why* one architecture beats another,
across all seven domains, under the clock. CollabForge trains exactly that.

A design-grade answer is three things at once — **the construct + the why + the source.** Produce all
three for a topic and you own it at exam level.

## The pipeline — Decode Exam Topics → Design-Grade Items

Every item in this repo is built by running a blueprint line through the same six stages:

1. **Decode the topic** — name the exact competency it tests.
2. **Concept & theory** — state it in one line you can re-derive from memory.
3. **Translate the requirement** — drivers → capacities, prerequisites, constraints.
4. **Cast a working scenario** — wrap it in a realistic customer ask.
5. **Build the item types** — multiple-answer, matrix, and drag-and-drop.
6. **Validate & anchor** — map to a domain and attach the Cisco doc that proves the answer.

Study each finished item in **three passes** — the concept, the worked example, the exam angle —
then close the page and re-derive the design rule from memory. See [METHODOLOGY.md](METHODOLOGY.md).

## What’s inside

```
CollabForge/
├── blueprint/ccie-collab-v3.1-design.yaml   # the decoded blueprint: 15 items × 7 domains
├── items/                                    # D1–D15, each as readable .md + machine-readable .yaml
├── item-types/
│   ├── matrix/                               # MX1–MX6 multiple-answer matrices
│   └── drag-and-drop/                        # DD1–DD3 + DDG1 ordering / topology items
├── templates/                                # item template + YAML schema for new items
├── tools/collabforge.py                      # runnable CLI: browse, drill, quiz yourself
├── GENERATE.md                               # spec to generate a NEW item with an AI agent
└── METHODOLOGY.md                            # the pipeline + how to study an item
```

## The item bank

| # | Design item | Item types |
|---|---|---|
| **D1** | [DTMF Relay & Media Interworking Design](items/D1-dtmf-relay-media-interworking-design.md) | Scenario Q&A ×4 · Matrix: MX1 |
| **D2** | [Collaboration APIs: AXL, UDS & SOAP Tooling](items/D2-collaboration-apis-axl-uds-soap-tooling.md) | Scenario Q&A ×4 · Matrix: MX2 |
| **D3** | [QoS & Call Admission Control Design](items/D3-qos-call-admission-control-design.md) | Scenario Q&A ×4 |
| **D4** | [Webex Calling: PSTN, Local Gateway, Dedicated Instance & UCM Interconnect](items/D4-webex-calling-pstn-local-gateway-dedicated-insta.md) | Scenario Q&A ×4 · Matrix: MX3, MX4, MX5, MX6 · DnD: DDG1 |
| **D5** | [Identity: SSO, Directory Sync & User Onboarding](items/D5-identity-sso-directory-sync-user-onboarding.md) | Scenario Q&A ×4 · DnD: DD1 |
| **D6** | [Webex Calling Routing: AA, Queues, Hunt Groups & Licensing](items/D6-webex-calling-routing-aa-queues-hunt-groups-lice.md) | Scenario Q&A ×4 |
| **D7** | [Edge: CUBE Multi-Tenancy, IPsec, Video Mesh & Expressway Clustering](items/D7-edge-cube-multi-tenancy-ipsec-video-mesh-express.md) | Scenario Q&A ×4 · Matrix: MX6 · DnD: DD2 |
| **D8** | [Contact Center: WxCC, Digital Channels & UCCX Positioning](items/D8-contact-center-wxcc-digital-channels-uccx-positi.md) | Scenario Q&A ×4 |
| **D9** | [SIP Signaling & Session Identity Design](items/D9-sip-signaling-session-identity-design.md) | Scenario Q&A ×4 |
| **D10** | [Media Negotiation & Path Optimization Design](items/D10-media-negotiation-path-optimization-design.md) | Scenario Q&A ×4 |
| **D11** | [Global Dial Plan & UCM Call Routing Design](items/D11-global-dial-plan-ucm-call-routing-design.md) | Scenario Q&A ×4 · DnD: DD3 |
| **D12** | [CUBE Dial-Peers, Normalization & Survivability Design](items/D12-cube-dial-peers-normalization-survivability-desi.md) | Scenario Q&A ×4 |
| **D13** | [Endpoint Registration & Security Design](items/D13-endpoint-registration-security-design.md) | Scenario Q&A ×4 |
| **D14** | [Media Resources & Meeting Security Design](items/D14-media-resources-meeting-security-design.md) | Scenario Q&A ×4 |
| **D15** | [Collab Apps: Voicemail, IM&P, Mobility & Recording Design](items/D15-collab-apps-voicemail-im-p-mobility-recording-de.md) | Scenario Q&A ×4 |

## Coverage — all seven blueprint domains

| Domain | Weight | Items |
|---|---|---|
| Domain 1 — Protocols & APIs | 10% | D1, D2, D9, D10 |
| Domain 2 — Infrastructure & QoS | 10% | D3 |
| Domain 3 — Call Control & Dial Plan | 20% | D6, D11, D12 |
| Domain 4 — Endpoints & User Management | 10% | D5, D13 |
| Domain 5 — Edge Services | 20% | D4, D7 |
| Domain 6 — Media Resources & Meetings | 15% | D14 |
| Domain 7 — Collaboration Apps & Services | 15% | D8, D15 |

## Quick start

```bash
# browse the bank
python3 tools/collabforge.py list

# open one item's concepts, scenario and questions
python3 tools/collabforge.py show D4

# drill yourself — a random question, weighted to a domain you choose
python3 tools/collabforge.py quiz --domain 5
```

No dependencies beyond Python 3 and PyYAML (`pip install pyyaml`).

## Make it yours

Fork it, then:
- **Edit `blueprint/ccie-collab-v3.1-design.yaml`** — retune which topics you drill.
- **Add items** with `templates/item-template.md` + `templates/item.schema.yaml`.
- **Generate new items** by handing [GENERATE.md](GENERATE.md) to an AI agent with a blueprint line.
- **Anchor everything** to an authoritative Cisco document — that’s what makes an answer defensible.

## A note on accuracy

Items reflect Cisco design guidance current at build time (CCIE Collaboration v3.1). Technical figures
(e.g. the 250-call Local Gateway registration ceiling, Dedicated Instance sizing) are teaching anchors —
**always re-verify against the latest Cisco documentation**, which is the real source of truth in the exam.

## License

MIT — see [LICENSE](LICENSE). Not an official Cisco product; a community study aid for CCIE Collaboration candidates.
