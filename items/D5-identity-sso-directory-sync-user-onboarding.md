# D5 · Identity: SSO, Directory Sync & User Onboarding

> **Blueprint domain:** Domain 4 — Endpoints & User Management  ·  **Item type coverage:** scenario Q&A, drag-and-drop (DD1)

**After this item you can:**

- Walk the SAML flow message by message and name every component
- Design UCM + ADFS SSO with the prerequisites that prevent the classic failures
- Choose the right Control Hub onboarding method and design out its risks

## Concepts & theory

_Read each topic in three passes — the **concept**, the **worked example**, the **exam angle** — then close the page and re-derive the design rule from memory._

### Topic 1 · SAML SSO: the flow, message by message

Three parties: the user's browser/client, the Service Provider (SP — each UCM/Unity/IM&P node, or Webex), and the Identity Provider (IdP — ADFS, Azure AD, Okta). The user hits the SP; the SP doesn't check the password — it redirects the browser to the IdP with a SAML AuthnRequest. The IdP authenticates the user (password, MFA, Kerberos) and returns a signed SAML assertion. The SP validates the signature and timestamps, maps the named user, and opens a session.

- SP never sees the password — that's the security point of SSO.
- Assertion = signed XML: subject (uid), conditions (NotBefore/NotOnOrAfter), audience.
- Trust = metadata exchange both ways: SP metadata → IdP, IdP metadata → SP.
- Cluster-wide agreement: one metadata set for all UCM nodes — the modern default.

**Worked example.** Webex App login walk: Webex App → UCM (SP) → HTTP 302 to https://adfs.corp.com with AuthnRequest → user does Kerberos/MFA at ADFS → ADFS POSTs signed assertion (subject kashif) back to UCM → UCM matches LDAP-synced userid kashif → session + OAuth tokens issued. The user typed their password at ADFS only — never at UCM.

**Exam angle.** Name the redirect target, what's inside the assertion, and which side validates it — free-text items use exactly these.

### Topic 2 · UCM + ADFS prerequisites — where SSO designs die

Four prerequisites decide success, and each maps to a classic failure. (1) Time: assertions carry validity windows; clock skew > a few minutes = 'assertion not yet valid'. (2) Identity mapping: the assertion's uid must equal UCM's LDAP-synced userid (sAMAccountName mismatch = valid login, unknown user). (3) Certificates: IdP signing cert must be trusted by the SP — and it EXPIRES on the IdP's schedule, not yours. (4) Recovery: a tested break-glass path before enforcement, or a bad change locks out every admin.

- NTP on UCM, IdP, and clients — same source, verified before go-live.
- uid mapping: assertion NameID/attribute ↔ LDAP-synced userid, exactly.
- Cert lifecycle runbook: IdP signing cert renewal = re-import metadata at SP.
- Recovery URL (https://ucm/ssosp/local) + local admin tested BEFORE enabling.

**Worked example.** Failure autopsy: SSO enforced Friday, fine all weekend, dead Monday 09:00 — 'NotBefore' rejections. Cause: ADFS VM restored Sunday night with drifted clock; assertions are 4 min in the future. The design artifact that prevents it: NTP alignment requirement + monitoring on skew + the recovery URL documented so admins could log in while fixing it. OAuth refresh tokens are the second exam favorite: without them the Webex App re-authenticates constantly; with them, sessions survive between IdP logins.

**Exam angle.** Map symptom→missed prerequisite: not-yet-valid→NTP; unknown user→uid mapping; sudden total failure→expired IdP cert; locked out→no recovery path.

### Topic 3 · Control Hub SSO: one IdP for the cloud org

Control Hub supports ONE SSO integration per organization: exchange metadata with the enterprise IdP, test with a single user, then enforce org-wide. After that, every Webex sign-in (app, web, devices' user auth) routes through the corporate IdP — same MFA, same conditional access. Critical design distinction: SSO covers AUTHENTICATION only. Creating, updating, licensing, and deactivating users is PROVISIONING — a separate mechanism (Directory Connector, Azure AD/SCIM) that the design must pair with SSO.

- One IdP per Control Hub org — multi-IdP estates need an IdP-side federation design.
- Domain claim/verification underpins routing users to your IdP.
- SSO ≠ lifecycle: pair with Directory Connector or SCIM for join/move/leave.
- Test-then-enforce: Control Hub provides a test flow before org-wide cutover.

**Worked example.** Design pairing for a 12k-user org: Azure AD is the IdP. Control Hub SSO via Azure AD metadata (auth + MFA + conditional access), PLUS Azure AD SCIM provisioning (auto-create users, assign licenses by group, deactivate leavers within the sync interval). A design that proposes SSO alone fails the 'leavers must lose access in 24 h' requirement — that's provisioning, not SSO.

**Exam angle.** Trap option: 'enable SSO to auto-provision users'. SSO never provisions; the verb in the requirement tells you which mechanism.

### Topic 4 · Onboarding methods: manual/CSV, Directory Connector, SCIM, domain claim

Four ways to populate a Control Hub org, chosen by where identity truth lives. Manual/CSV: admin-driven, fine for pilots and small orgs. Directory Connector: on-prem AD is authoritative — a Windows service syncs selected OUs/attributes to Webex on schedule. Azure AD/SCIM: cloud directory is authoritative — push provisioning with group-based licensing. Domain claim: claim/verify your domains to take control of existing self-signed-up 'consumer' accounts on your domain and route them into the org.

- Decision = who owns identity truth: nobody (manual) / on-prem AD (Connector) / Azure AD (SCIM).
- Connector: scheduled sync, attribute mapping, OU scoping, dry-run reports.
- SCIM: near-real-time, group-driven licensing, no on-prem footprint.
- Domain claim first in brownfield: discover and convert existing accounts before bulk-adding.

**Worked example.** Brownfield walk: company merges in a startup whose staff already use free Webex accounts on startup.com. Design order: (1) claim startup.com, (2) convert/claim those users into the org, (3) connect the merged AD via Directory Connector for lifecycle, (4) switch auth to corporate SSO. Doing step 3 before step 1 creates duplicate identities — the item's distractor.

**Exam angle.** Sequence matters in brownfield items: claim domain → convert users → connect directory → enforce SSO.

### Topic 5 · Directory Connector mechanics & the deletion safety design

Directory Connector runs on a domain-joined Windows server, reads AD via LDAP on a schedule, maps attributes (mail→email, displayName, etc.), and pushes adds/updates/DELETES to the Webex identity service. Deletion is the sharp edge: whatever falls out of the synced scope is deactivated in the cloud. A mis-scoped OU filter or a re-organized AD tree can deactivate thousands of working users in one sync cycle.

- Full sync vs incremental: schedule fulls off-hours; incrementals frequently.
- Scoping by OU/LDAP filter — review every AD reorg against the filter.
- Dry-run report BEFORE first sync and after scope changes — non-negotiable in the design.
- HA: second connector instance in cold standby; same config, one active.

**Worked example.** Incident to design against: an AD admin moves 2,000 users from OU=Staff to OU=Employees; the connector filter still says OU=Staff. Next sync: 2,000 cloud users deactivated mid-day. Mitigations that belong in the design doc: deletion threshold/alerting, dry-run after any AD change, change-control linkage between AD ops and collab ops, and a documented re-activation runbook.

**Exam angle.** 'What safeguard prevents mass deactivation?' — scoping review + dry-run + deletion threshold. All three, not one.

## Decide fast — requirement → design answer

| When the brief says… | The design answer is… |
|---|---|
| Pilot, <300 users, no AD | Manual / CSV |
| On-prem AD authoritative | Directory Connector (+ dry-run) |
| Cloud-first, Azure AD | SCIM provisioning + group licensing |
| Existing consumer accounts on your domain | Domain claim → convert |
| Webex App re-auth loops after SSO | OAuth refresh tokens |

## Worked design scenario

**The customer ask.** 12,000 users, on-prem AD + ADFS, UCM today, Webex App next quarter. Security mandates corporate MFA for every client; HR demands leavers lose all access within 24 hours; 800 staff already use personal Webex accounts on the corporate domain.

**The model answer.**

- UCM: cluster-wide SAML SSO to ADFS — NTP alignment, uid mapping (sAMAccountName↔userid), recovery URL tested, OAuth refresh tokens on.
- Domain claim first; convert the 800 consumer accounts into the org before bulk onboarding.
- Directory Connector from the authoritative AD OUs (dry-run, deletion threshold, HA standby) → 24 h leaver SLA met by sync schedule.
- Control Hub SSO against the same ADFS → one MFA policy across the Webex App and web.
- Runbooks in the design: IdP cert renewal, break-glass, AD-reorg → filter review.

## Check yourself — exam-style questions

_Multiple-answer (select all that apply). Try each in ~2 minutes before revealing the key._

**Q1. SSO works for ccmadmin but the Webex App re-authenticates hourly. What's missing, and where is it enabled?**

<details><summary>Answer key</summary>

- ✅ OAuth with Refresh Login Flow (UCM enterprise parameter)
- ✅ Soft clients then silently renew via refresh token — no hourly re-auth
- ⬜ Extend the IdP session lifetime
- ⬜ Shorten the SAML assertion validity window

</details>

**Q2. Monday 09:00: every SSO login fails 'assertion not yet valid'. Root cause and the two design controls that prevent it?**

<details><summary>Answer key</summary>

- ✅ Clock skew — the IdP clock drifted so NotBefore is in the future
- ✅ Enforce NTP on both the IdP and the SP
- ✅ Monitor/alert on IdP time drift
- ⬜ Increase the skew tolerance to 30 minutes

</details>

**Q3. Leavers must lose Webex access in 24 h. Which mechanism delivers that — and why is SSO alone the wrong answer?**

<details><summary>Answer key</summary>

- ✅ Automated deprovisioning via Directory Connector / SCIM
- ✅ SSO governs authentication, not licence/identity lifecycle
- ⬜ Disable the user in the IdP only
- ⬜ Delete the user manually in Control Hub each time

</details>

**Q4. An AD reorg deactivates 2,000 cloud users at noon. Name the three safeguards the design should have contained.**

<details><summary>Answer key</summary>

- ✅ Connector OU/LDAP filter reviewed under AD change control
- ✅ A safety limit / avoid-deletion threshold on the sync
- ✅ Alerting on a large deactivation delta before commit
- ⬜ No safeguard is possible because AD is authoritative

</details>

## Interactive items for this topic

[DD1](../item-types/drag-and-drop/DD1.md)

---
_Source of truth: anchor every answer to the authoritative Cisco document. See the item YAML for source URLs. Part of **CollabForge** — the CCIE Collaboration Design-item bank._