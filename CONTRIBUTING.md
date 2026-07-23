# Contributing to CollabForge

New items and fixes welcome — especially fresh worked scenarios and better distractors.

1. Start from `templates/item-template.md` and `templates/item.schema.yaml`, or generate a draft with
   `GENERATE.md`.
2. Every factual claim must be **anchored to an authoritative Cisco document** (add the URL to the
   item YAML `sources:`). Community blogs are not sources of truth.
3. Distractors should be **plausible designs that fail on the brief**, not obviously wrong answers.
4. Run `python3 tools/collabforge.py check` to validate your YAML before opening a PR.
5. Keep the exam version current — note the blueprint revision your item targets.

This is a community study aid, not an official Cisco product, and contains no exam content — only
original practice built from the public blueprint and public documentation.
