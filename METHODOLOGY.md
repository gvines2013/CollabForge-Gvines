# The CollabForge Methodology

## Design-grade = construct + why + source

A design answer is never just the setting. It is:
- **The construct** — the Cisco building block that solves it (a Standard Local Route Group, a
  certificate-based Local Gateway, a partition/CSS pairing).
- **The why** — the requirement in the brief that makes *this* construct correct, not merely one that works.
- **The source** — the authoritative Cisco document that settles a close call.

## The differentiator constraint

When two options both look valid, stop comparing options and go back to the brief. A single keyword —
*OPEX reduction, end-to-end encryption, minimal user disruption, no on-prem assets* — is the tie-breaker.
Read the brief first and write the facts down **before** you look at a single option, then eliminate
against the brief, not against the docs. *Supported in the documentation ≠ right for this customer.*

## The pipeline (how every item is built)

| Stage | What you do |
|---|---|
| 1 · Decode the topic | Name the exact competency the blueprint line tests. |
| 2 · Concept & theory | One or two sentences you can re-derive from memory. |
| 3 · Translate the requirement | Turn drivers into capacities, prerequisites, constraints. |
| 4 · Cast a working scenario | Wrap the need in a realistic customer ask. |
| 5 · Build the item types | Multiple-answer, matrix, drag-and-drop. |
| 6 · Validate & anchor | Map to a domain; attach the Cisco doc that proves it. |

## How to study an item — three passes

1. **Concept** — read the theory once.
2. **Worked example** — see it applied to a real situation.
3. **Exam angle** — learn the symptom-to-design mapping the exam hides in a brief.

Then **close the page and re-derive the design rule from memory.** That last step is the one most
people skip, and the one that makes it stick.

## Item anatomy

Each `items/Dxx-*.md` contains: learning objectives · five concept topics (concept / worked example /
exam angle) · a *Decide fast* requirement→answer table · a worked design scenario (customer ask +
model answer) · four multiple-answer questions with answer keys · links to related matrix and
drag-and-drop items. The paired `.yaml` is the machine-readable version (used by `tools/collabforge.py`).
