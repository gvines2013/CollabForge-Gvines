# Generating a new design item

Hand this spec, plus **one blueprint line**, to an AI agent (or use it yourself). The agent should
return a Markdown item and a YAML item that match the files in `items/`.

## Prompt

> You are building a CCIE Collaboration **Design module** practice item. Run the blueprint topic
> below through the CollabForge pipeline and output (a) a Markdown item and (b) a YAML item that
> validate against `templates/item.schema.yaml`.
>
> **Blueprint topic:** `<paste one line, e.g. 5.12 Premises-based PSTN for Webex Calling>`
>
> Rules:
> 1. **Decode** the topic — state the competency in one sentence.
> 2. Write **five concept topics**. Each has a `concept` (2–4 sentences, re-derivable), 3–4 `bullets`,
>    a `worked_example`, and an `exam_angle` (the symptom→design mapping the exam hides).
> 3. Add a **Decide fast** table: 4–6 `requirement → answer` pairs.
> 4. Write **one worked scenario**: a realistic `customer_ask` and a 4–5 point `model_answer`.
> 5. Write **four multiple-answer questions**. Each has 4 options; mark each `correct: true|false`.
>    At least one distractor must be a plausible-but-wrong design (a “technically works” trap).
> 6. **Anchor** every factual claim to an authoritative Cisco document (URL in the YAML `sources`).
> 7. Keep numbers exact (capacities, ceilings, prerequisites) — they are the discriminators.

## Quality bar

- A candidate who reads only the `concept` + `exam_angle` should be able to answer the questions.
- Every question must be defensible from a Cisco doc — no “because I said so”.
- Distractors should fail on the **brief**, not on being obviously wrong.
