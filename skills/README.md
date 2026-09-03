# skills/

Claude Code skills developed alongside the eDNA work. Not part of the published site.

## edna-manuscript

A **domain overlay** that binds eDNA Knowledge Base grounding to manuscript writing and
review. It is deliberately thin: it does not reimplement a writing system, it supplies
domain authority and one gate — no load-bearing scientific claim enters a manuscript
unless it resolves to a validated KB chunk ID or is explicitly marked `[UNGROUNDED]`.

```
edna-manuscript/
├── SKILL.md                        the overlay
├── references/okf-mapping.md       eDNA KB <-> Open Knowledge Format v0.2 crosswalk
├── scripts/kb_to_okf.py            read-only OKF conformance reporter
└── tests/fixtures/kb_root/         synthetic KB the script is tested against
```

### Status

**Prototype. Not validated against the live KB.** The overlay was written against the
published behavior of `edna-kb` and `edna-kb-audit` (their `SKILL.md` files) and against
the `academic-writing-skills` overlay contract, both read directly. It has not been run
on a real manuscript, and the KB folder was not connected in the session that produced
it. `kb_to_okf.py` is tested only against the synthetic fixtures in `tests/fixtures/`,
whose frontmatter shape is inferred from `edna-kb-audit`'s documented fields — if the
real chunks differ, the field-coverage numbers will be wrong until the crosswalk is
corrected.

### Composition

Designed to sit on top of a manuscript-integrity base — `academic-writing-skills` /
`paper-review` ([WenyuChiou](https://github.com/WenyuChiou/academic-writing-skills), MIT)
— using that base's documented overlay contract, which requires each overlay rule to be
classified and forbids promoting domain conventions into universal requirements.
`SKILL.md` carries that classification table. The overlay degrades gracefully: without
the base installed it still grounds claims, it just has no host for the lifecycle and
release gates, and it must say so rather than claim checks that never ran.

### Install

```bash
cp -r skills/edna-manuscript ~/.claude/skills/
```

## Open Knowledge Format

`references/okf-mapping.md` documents the finding that motivated this directory. OKF is
an open, vendor-neutral spec from Google Cloud (v0.1 2026-06-12, v0.2 2026-07-25) that
represents knowledge as a directory of markdown files with YAML frontmatter. v0.2 added
the trust-signal families — provenance, trust, lifecycle, attestation — and those map
almost one-to-one onto fields the eDNA KB already maintains (`sources`, `last_verified`,
`review_after`).

The KB arrived at this shape independently. Conformance is therefore additive rather
than a migration, and it buys a deterministic validator with a CI gate, a read-only MCP
server for graph retrieval instead of grep, and a container for attested computations.
It buys nothing epistemic: find-then-validate, the relevance and distant-field gates,
IP confidentiality, and ledger dedupe all remain the KB's own responsibility. The
mapping document is explicit about both halves, and about the one structural friction
(OKF makes the file path the concept ID; the KB cites short chunk-ID tokens).

Toolchain: [scaccogatto/okf-skills](https://github.com/scaccogatto/okf-skills) (MIT).
Nothing has been installed and no KB content has been modified.

### Running the conformance reporter

```bash
python3 skills/edna-manuscript/scripts/kb_to_okf.py <kb_root>          # report
python3 skills/edna-manuscript/scripts/kb_to_okf.py <kb_root> --json   # machine-readable
python3 skills/edna-manuscript/scripts/kb_to_okf.py <kb_root> --emit EB08
```

Read-only, stdlib-only, never writes to the KB. Exits non-zero when it finds duplicate
chunk IDs or files whose names encode none.
