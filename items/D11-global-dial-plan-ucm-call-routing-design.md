# D11 · Global Dial Plan & UCM Call Routing Design

> **Blueprint domain:** Domain 3 — Call Control & Dial Plan  ·  **Item type coverage:** scenario Q&A, drag-and-drop (DD3)

**After this item you can:**

- Design a +E.164 globalized core with localized user dialing habits at the edges.
- Build partitions and calling search spaces that enforce class-of-service cleanly.
- Use translation/transformation patterns, urgent priority and LRGs for site routing.
- Apply Local Route Groups and Emergency Location Groups for tail-end-hop-off and E911.

## Concepts & theory

_Read each topic in three passes — the **concept**, the **worked example**, the **exam angle** — then close the page and re-derive the design rule from memory._

### Topic 1 · Globalization vs localization

Best practice routes the core in +E.164 (globalized) and converts to and from local dialing habits only at the edges. Incoming calling numbers are globalized for a consistent format; called numbers are localized to the gateway just before egress.

- Globalize the calling party (so callbacks from call history work everywhere) using incoming called/calling party settings.
- Localize the called party at the route pattern / gateway with called-party transformations.
- One global pattern set + per-site transforms beats per-site dial plans.

**Worked example.** Missed-call callbacks fail at a branch because history stored a 4-digit number. Globalizing the calling party to +E.164 on ingress makes every logged number diallable from any device.

**Exam angle.** A 'callback from history fails' symptom is a globalization-of-calling-party design gap.

### Topic 2 · Partitions and Calling Search Spaces

A partition is a group of dialable patterns; a CSS is an ordered list of partitions a device may reach. Together they implement class of service: what a phone can call is the intersection of its line/device CSS and the partitions that hold each pattern.

- Order matters: the first matching pattern across the CSS wins (with urgent priority as the override).
- Line/device CSS combine — design which carries class-of-service vs which carries device/feature reachability.
- Block patterns (e.g., 1-900) live in a partition only privileged CSSes include.

**Worked example.** Lobby phones can dial international numbers. The device CSS included an Intl partition; removing it (or moving Intl to a privileged CSS only) enforces the intended class of service without touching patterns.

**Exam angle.** Class-of-service items are solved by CSS/partition membership, not by editing route patterns.

### Topic 3 · Translation & transformation patterns, urgent priority

Translation patterns re-write the called number and re-route through a CSS before route selection; transformation patterns only re-format calling/called numbers without routing. Urgent priority forces an immediate match, stopping interdigit timeout.

- Use translation patterns for abbreviated/feature dialing (e.g., 0 → operator) and to steer into a different CSS.
- Mark variable-length or overlapping patterns urgent so a complete short number routes without waiting (e.g., emergency).
- Transformations (calling/called party) tidy presentation and localization at the edge.

**Worked example.** Dialing 911 waits for interdigit timeout because 9.11 overlaps 9.1[2-9]XX. Marking the emergency translation pattern urgent removes the delay — a safety-critical fix.

**Exam angle.** Any 'dialing X is slow / waits' item points at urgent priority on an overlapping pattern.

### Topic 4 · Local Route Groups and path selection

A Local Route Group decouples route patterns from physical gateways: the route pattern points at the LRG 'Standard Local Route Group', and the device pool binds that to the site's actual gateway. One PSTN pattern then serves every site.

- Device Pool → Local Route Group setting selects the egress gateway per site.
- Collapses dozens of site route patterns into one globalized pattern + LRG.
- Path selection adds route lists/groups for priority and overflow between gateways.

**Worked example.** A 50-site org had 50 PSTN route patterns. Re-pointing one +E.164 pattern to Standard Local Route Group and setting each device pool's LRG yields local breakout everywhere from a single pattern.

**Exam angle.** 'Calls egress at the wrong site / one pattern for all sites' is a Local Route Group design.

### Topic 5 · Emergency call routing: ELG and E911 design

Emergency calls must egress the gateway nearest the caller and present a location-accurate callback number. Emergency Location (ELIN) groups, device-pool LRG and (optionally) Emergency Responder map a device to the right PSAP trunk and ELIN.

- Egress the local gateway via LRG so the PSAP sees a local origin.
- Present a valid ELIN/callback DID so emergency services can call back.
- Mark the emergency pattern urgent and test from every device type.

**Worked example.** A remote-site phone's 911 call exits the HQ gateway, reaching the wrong PSAP. Binding the site device pool's Local Route Group to the local gateway and assigning the correct ELIN fixes jurisdiction and callback.

**Exam angle.** E911 'wrong PSAP / wrong callback' items combine LRG egress + ELIN, never a single checkbox.

## Decide fast — requirement → design answer

| When the brief says… | The design answer is… |
|---|---|
| Consistent core number format | Globalize to +E.164, localize at edge |
| Enforce class of service | Partition + CSS membership |
| Short/overlapping number is slow | Urgent priority on the pattern |
| One PSTN pattern for all sites | Standard Local Route Group + device pool |
| 911 to the correct PSAP + callback | Local gateway via LRG + ELIN |

## Worked design scenario

**The customer ask.** A 40-site enterprise has per-site route patterns, slow 911 dialing, callbacks from history that fail at branches, and lobby phones that can dial international. Re-architect the dial plan.

**The model answer.**

- Globalize calling/called to +E.164 in the core; localize called-party at each gateway so history callbacks work and formats are uniform.
- Replace per-site patterns with one +E.164 pattern pointing at Standard Local Route Group; set each device pool's LRG for local breakout.
- Mark the emergency translation pattern urgent and route 911 out the local gateway with the correct ELIN/callback.
- Fix class of service through CSS/partition membership — remove the Intl partition from public-area device CSSes.

## Check yourself — exam-style questions

_Multiple-answer (select all that apply). Try each in ~2 minutes before revealing the key._

**Q1. An enterprise wants ONE PSTN route pattern that breaks out locally at every site. Which UCM construct makes this possible and where is the per-site choice made?**

<details><summary>Answer key</summary>

- ✅ The route pattern targets Standard Local Route Group
- ✅ Each site's Device Pool maps the LRG to its local gateway
- ✅ LRGs decouple routing logic from physical gateways
- ⬜ Build a separate route pattern + route list per site

</details>

**Q2. Dialing 911 waits several seconds before routing. What is the cause and the one-setting fix?**

<details><summary>Answer key</summary>

- ✅ An overlapping pattern triggers the interdigit timeout
- ✅ Mark the 911 pattern with Urgent Priority
- ✅ Urgent priority forces an immediate match
- ⬜ Shorten the global interdigit timer

</details>

**Q3. Callbacks from a branch user's call history fail, though the same numbers dial fine when typed in full. Which design principle was missed?**

<details><summary>Answer key</summary>

- ✅ Globalize the calling party to +E.164 at ingress
- ✅ History then stores diallable +E.164 numbers
- ✅ Localization happens only at egress
- ⬜ Edit each branch's translation patterns for callbacks

</details>

**Q4. Public lobby phones can place international calls. Without touching any route pattern, how do you enforce the correct class of service?**

<details><summary>Answer key</summary>

- ✅ Remove the international partition from the lobby phones' CSS
- ✅ Class of service = the intersection of CSS and partition
- ✅ Place Intl patterns in a partition only privileged CSSes include
- ⬜ Delete or block the international route pattern

</details>

## Interactive items for this topic

[DD3](../item-types/drag-and-drop/DD3.md)

---
_Source of truth: anchor every answer to the authoritative Cisco document. See the item YAML for source URLs. Part of **CollabForge** — the CCIE Collaboration Design-item bank._