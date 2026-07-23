# D13 · Endpoint Registration & Security Design

> **Blueprint domain:** Domain 4 — Endpoints & User Management  ·  **Item type coverage:** scenario Q&A

**After this item you can:**

- Trace endpoint registration on-prem, via MRA, and to the cloud.
- Explain Security By Default — CTL, ITL and TVS — and how trust is bootstrapped.
- Design mixed mode for encrypted signalling/media and know when it is required.
- Choose SIP OAuth vs CAPF/LSC for endpoint authentication and certificate lifecycle.

## Concepts & theory

_Read each topic in three passes — the **concept**, the **worked example**, the **exam angle** — then close the page and re-derive the design rule from memory._

### Topic 1 · Registration paths: on-prem TFTP, MRA, cloud

An endpoint must find its config and call agent. On-prem it uses DHCP option 150 → TFTP for its config file then registers to UCM. MRA uses service discovery (_collab-edge / _cisco-uds SRV) through Expressway. Cloud devices register to Webex.

- DHCP opt 150 (or Alternate TFTP) points the phone at the TFTP/UCM nodes.
- MRA: external _collab-edge SRV → Expressway-E → C → UCM; no VPN needed.
- Hybrid endpoints can be UCM-registered yet Webex-managed — define the calling anchor explicitly.

**Worked example.** Home-office phones won't register. External DNS lacked the _collab-edge SRV, so MRA service discovery failed. Publishing the SRV record restores registration with no VPN.

**Exam angle.** 'Remote phone can't register, no VPN' = MRA SRV/Expressway service-discovery design.

### Topic 2 · Security By Default: CTL, ITL and TVS

SBD secures phone trust automatically. The Identity Trust List (ITL) is signed by the UCM TFTP (ITLRecovery/CallManager) and tells the phone which servers to trust; the Certificate Trust List (CTL) is used in mixed mode; the Trust Verification Service (TVS) lets a phone verify unknown certificates without a CTL token.

- ITL is installed on first contact and pins the phone to the cluster's trust anchors.
- TVS answers 'can I trust this cert?' so phones accept new services without re-tokening.
- ITL/CTL mismatches after a cluster change cause 'config/registration rejected' until reset.

**Worked example.** After a publisher rebuild phones show 'No trust list installed' and fail config. The ITL signer changed; deleting the stale ITL (or using ITLRecovery) re-establishes trust cluster-wide.

**Exam angle.** Post-migration 'trust list' or 'config rejected' symptoms are ITL/CTL/TVS questions.

### Topic 3 · Mixed mode: encrypted signalling and media

Mixed mode enables authenticated/encrypted device security profiles (TLS signalling + SRTP media). It requires the CTL established via the Tokenless CTL (CLI) or USB eTokens and per-device encrypted security profiles.

- Mixed mode is required for SRTP/TLS to endpoints and for some compliance mandates.
- Device security profile (Encrypted) + LSC is what actually secures a given phone.
- Plan certificate lifecycle (CAPF) before flipping mixed mode at scale.

**Worked example.** A compliance requirement mandates encrypted calls. Enable mixed mode, assign encrypted device security profiles, and issue LSCs via CAPF; verify SRTP with 'show' on the gateway/phone.

**Exam angle.** If the requirement says 'encrypted signalling AND media to phones', mixed mode is mandatory, not optional.

### Topic 4 · SIP OAuth vs CAPF/LSC

Endpoint authentication can use certificates (LSC issued by CAPF) or tokens. SIP OAuth lets endpoints authenticate with OAuth tokens (from the IdP) instead of an LSC, simplifying secure registration — especially over MRA without CAPF certificate enrolment.

- CAPF issues/renews the LSC that identifies a phone; the LSC underpins encrypted profiles and 802.1X.
- SIP OAuth uses refresh/access tokens so phones register securely without an LSC — great for MRA.
- Choose per requirement: certificate-based identity (LSC) vs token-based (OAuth) — and plan renewal either way.

**Worked example.** Securing MRA phones via CAPF over the edge was painful. Enabling SIP OAuth lets Jabber/phones register with tokens, removing the LSC enrolment hurdle while keeping TLS.

**Exam angle.** 'Secure MRA registration without certificate enrolment' points to SIP OAuth; encrypted-profile identity points to CAPF/LSC.

### Topic 5 · Hardening endpoints: 802.1X, TVS scaling, lifecycle

Beyond registration, endpoints are hardened with 802.1X (using the LSC as the supplicant identity), disabled web/SSH access, and a planned certificate lifecycle so nothing expires silently.

- LSC = device identity for 802.1X and encrypted security profiles.
- Disable unused phone services (web access, PC port, SSH) per security policy.
- Track CAPF/LSC and ITLRecovery expiry — expired trust anchors brick registration.

**Worked example.** Phones drop off the network at a site running 802.1X after an LSC expired. A CAPF renewal schedule and monitoring prevent the silent expiry that caused the outage.

**Exam angle.** Lifecycle items test that you plan renewal of LSC/ITLRecovery/CTL, not just initial enrolment.

## Decide fast — requirement → design answer

| When the brief says… | The design answer is… |
|---|---|
| Remote phone, no VPN | MRA via Expressway + _collab-edge SRV |
| Phone shows 'no trust list' | Fix ITL/TVS (ITLRecovery) |
| Encrypted signalling + media to phones | Mixed mode + encrypted profile + LSC |
| Secure MRA without cert enrolment | SIP OAuth (token-based) |
| 802.1X device identity | CAPF-issued LSC |

## Worked design scenario

**The customer ask.** A regulated customer needs encrypted calls to phones, secure remote registration without VPN, and recently saw phones fail after a UCM publisher rebuild. Design registration and endpoint security.

**The model answer.**

- Enable mixed mode with encrypted device security profiles and SRTP/TLS; issue and schedule renewal of LSCs via CAPF.
- Provide remote access via MRA (Expressway-E/C, _collab-edge SRV) and use SIP OAuth so remote phones register securely without certificate enrolment pain.
- Re-establish SBD trust after the rebuild using ITLRecovery/TVS so phones accept the new signer; document the procedure.
- Harden endpoints (802.1X with LSC, disabled web/PC port) and track all trust-anchor expiries to avoid silent outages.

## Check yourself — exam-style questions

_Multiple-answer (select all that apply). Try each in ~2 minutes before revealing the key._

**Q1. Remote-worker phones cannot register and the customer refuses VPN. What registration design applies and what DNS record is pivotal?**

<details><summary>Answer key</summary>

- ✅ Mobile and Remote Access via Expressway-E / C
- ✅ The external _collab-edge SRV bootstraps service discovery
- ✅ MRA needs no VPN
- ⬜ Open SCCP/SIP ports straight to UCM through the firewall

</details>

**Q2. After a publisher rebuild, phones display 'No trust list installed' and reject their config. Which SBD components are involved and how is trust restored?**

<details><summary>Answer key</summary>

- ✅ ITL (and CTL in mixed mode), validated by TVS
- ✅ Restore trust with ITLRecovery
- ✅ The ITL signer changed on the rebuild
- ⬜ Factory-reset every phone manually

</details>

**Q3. The design must secure MRA-registered phones but the team wants to avoid CAPF certificate enrolment over the edge. What authenticates the endpoints instead?**

<details><summary>Answer key</summary>

- ✅ SIP OAuth — token-based secure registration
- ✅ No LSC / CAPF enrolment required
- ✅ Well-suited to MRA where edge enrolment is awkward
- ⬜ Insist on an LSC via CAPF for every phone

</details>

**Q4. A compliance mandate requires both signalling and media to phones to be encrypted. What cluster mode and per-device settings are mandatory?**

<details><summary>Answer key</summary>

- ✅ Enable mixed mode (establish the CTL)
- ✅ Assign an Encrypted device security profile with an LSC
- ✅ Result: TLS signalling + SRTP media to the phone
- ⬜ Enable an encrypted profile while the cluster stays non-secure

</details>

---
_Source of truth: anchor every answer to the authoritative Cisco document. See the item YAML for source URLs. Part of **CollabForge** — the CCIE Collaboration Design-item bank._