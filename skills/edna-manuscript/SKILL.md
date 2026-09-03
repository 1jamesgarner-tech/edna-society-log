---
name: edna-manuscript
description: Domain overlay that binds eDNA Knowledge Base grounding to manuscript writing and review. Use when drafting, revising, reviewing, or preparing for submission any manuscript, thesis chapter, abstract, reviewer response, or proposal whose scientific claims fall in eDNA scope — eDNA methods, sampling and survey design, primers and markers, occupancy/RMT/EcoCASH/eDITH modeling, qPCR/ddPCR/LOD/LOQ, metabarcoding bioinformatics, New England aquatic communities, or the Monument River, Vinica Brook, Connecticut River sturgeon, Jones River, and Town Brook projects. Routes every load-bearing claim to a validated KB chunk ID before it is allowed into prose, and reports claims the KB cannot support.
---

# eDNA Manuscript Overlay

This skill is an **overlay**, not a writing system. It supplies domain grounding to a
manuscript-integrity base and adds one gate that base does not have: no load-bearing
scientific claim enters the manuscript unless it resolves to a validated KB chunk or is
explicitly marked as unsupported.

## Composition

Compose with, in this order:

1. **`edna-kb`** — the authority for domain facts. Its `PROJECT_INSTRUCTIONS.md` and
   `PROJECT_MEMORY.md` are the source of truth and win over this file on any conflict.
2. **A manuscript-integrity base** — `academic-writing-skills` / `paper-review`
   (WenyuChiou) if installed, which supplies lifecycle, change-impact classes, claim-scope
   control, and release gates. If it is not installed, this overlay still functions; it
   simply has no host for its integrity gates, and you should say so rather than
   pretending the manuscript passed checks that were never run.
3. **`edna-kb-audit`** — invoked only when the manuscript surfaces a KB gap or conflict.
   Writing a manuscript never edits the KB as a side effect.

Under that base's overlay contract, classify what this file supplies:

| Rule | Overlay class |
|---|---|
| Chunk-ID resolution before a claim is drafted | domain check |
| Independent-sources confidence signalling | domain check |
| Distant-field applicability caveats | domain check |
| TaxaFloc non-disclosure | project state (and a research-integrity constraint) |
| Project facts, sites, locked wording | project state |

None of these are universal scientific requirements, and none may be presented as such
in a review of someone else's manuscript. Per the base's precedence order, safety,
ethics, and research-integrity constraints outrank everything here; verified evidence
and authoritative project facts outrank the user's current phrasing preference; venue
requirements outrank domain convention.

## The grounding gate

Before drafting or approving any sentence carrying a **load-bearing claim** — a
parameter, threshold, equation, detection limit, species-level assertion, methodological
requirement, or defensibility statement:

1. **Route.** Identify candidate chunk IDs via `edna-kb` Step 2. Do not answer from
   `KB_INDEX.md` alone; retrieve chunk bodies.
2. **Locate the span.** Find the exact supporting text inside the chunk. A chunk ID that
   merely covers the topic is not support for a specific number.
3. **Classify the claim's support:**
   - **grounded** — chunk span found. Carry the chunk ID in the drafting notes.
   - **single-source** — supported, but by one primary reference however many chunks
     repeat it. Draft it with hedged scope and flag for independent verification.
   - **KB-silent** — no validated coverage. Either draft it explicitly marked
     `[UNGROUNDED]` for author decision, or leave the claim out. Never quietly supply it
     from training knowledge; the base's authority gate and `edna-kb` Step 3 both
     forbid this, and here the cost is a fabricated citation in a submitted paper.
4. **Check independence before signalling confidence.** Chunks cross-cite. Three chunks
   echoing one reference is evidence pseudoreplication, not three-source support —
   compare the chunks' `sources:` before writing "well established."

## Claim-scope discipline

The base skill distinguishes direction, magnitude, uncertainty, significance,
equivalence, causation, mechanism, prediction, and generalizability. Two eDNA-specific
traps recur and are worth checking every time:

- **Detection is not abundance, and non-detection is not absence.** Any sentence moving
  from a read count or Cq to an abundance or occupancy statement needs the model that
  licenses it, cited, with its assumptions stated.
- **Distant-field borrowing.** When a claim rests on clinical, food-safety, forensic, or
  bench molecular biology work, label the field of origin, state that its thresholds and
  interpretations are not necessarily 1:1 applicable to field eDNA without validation,
  ground it in an in-field eDNA study, and name the residual validation gap. Adjacent
  aquatic and environmental molecular ecology does not trigger this — only materially
  different assumptions do.

## Confidentiality

TaxaFloc device architecture (solid-phase La³⁺ capture, radial flow, EDTA elution) must
not appear in any manuscript, figure, caption, supplement, preprint, or reviewer
response. Depth is available for the user's own drafting; public disclosure is not.
Flag whenever a passage approaches this boundary rather than silently softening it —
silent softening loses the author's ability to make the disclosure decision. Treat a
manuscript, a preprint server, and a grant narrative as public-facing.

## When the manuscript and the KB disagree

The manuscript's own new results outrank the KB — a chunk is prior validated knowledge,
not a constraint on new findings. When drafting surfaces a genuine conflict:

1. Draft the manuscript claim from the study's own evidence.
2. Raise a KB Conflict Note naming the chunk ID and the disagreement.
3. Offer to run `edna-kb-audit` on that chunk **after** the drafting session. Do not
   interrupt manuscript work to edit the KB, and never edit a chunk to match a draft
   that has not been through review.

## Reporting

At the end of any drafting, review, or revision pass, report:

- **Chunks Referenced** — every chunk ID the prose now depends on.
- **Ungrounded claims** — each `[UNGROUNDED]` span, with what would be needed to ground it.
- **Single-source claims** — flagged for independent verification.
- **KB gaps and conflicts surfaced**, and whether an audit was recommended.
- **Confidentiality flags** raised.
- Which overlay was applied and which base gates actually ran, per the base's
  functional-completeness retrospective. Report only checks actually performed.
