# eDNA KB ↔ Open Knowledge Format (OKF) crosswalk

Status: **design document, not yet applied to the live KB.** Verified against the OKF
v0.2 field families and the `okf-skills` toolchain; not yet run against real L0/L1 chunks.

## Why OKF is relevant

OKF is an open, vendor-neutral specification from Google Cloud (v0.1 published
2026-06-12; v0.2 on 2026-07-25) that represents knowledge as a directory of markdown
files with YAML frontmatter, cross-linked into a graph. v0.2 is the version that
matters here: it added the optional trust-signal families — provenance, trust,
freshness/lifecycle, and attestation.

That is the same shape the eDNA KB already has. The KB was built independently and
arrived at a near-identical structure: one concept per file, YAML frontmatter carrying
`sources:`, `last_verified:`, `review_after:`, a change history, and a deterministic
integrity checker. OKF is therefore not a migration away from the KB design — it is a
published spec the KB can *claim conformance with*, and thereby inherit tooling.

## Field crosswalk

| KB field (from `edna-kb-audit`) | OKF v0.2 | Family | Fit |
|---|---|---|---|
| chunk ID (`EB08`, `S8`, `STAT-Occ01`) | concept ID = bundle-relative path minus `.md` | identity | **friction — see below** |
| `sources:` | `sources[]` | provenance | direct |
| `last_verified:` + `verified_by:` | `verified[]` entries | trust | direct, and richer |
| `review_after:` | `stale_after` | lifecycle | direct |
| `revision_note:` (dated, appended in file) | `log.md`, newest first, + `last_modified` | provenance | direct, but relocates history |
| `topics:` | `tags` | — | direct |
| L0 vs L1 layer | `type` (the one required field) | — | direct |
| `sources_verified:` | no equivalent | — | keep as KB extension |
| `audit_ledger.json` (seen/added/rejected) | no equivalent | — | stays KB-side |
| `kb_lib.py check` | `okf_validate.py --strict` | — | complementary, not a replacement |

### The one real friction: chunk ID vs path-as-ID

OKF makes the **file path** the concept's unique identifier. The KB makes a **short
token** the identifier (`EB08`) and encodes it as a filename prefix
(`L0/L0-EB08_….md`). These are not the same thing, and the difference is load-bearing:
every KB-grounded answer cites chunk IDs, and `PROJECT_INSTRUCTIONS.md` §2 requires it.

Resolution — keep both, do not renumber anything:

- The OKF concept ID becomes the existing path minus the extension, e.g.
  `L0/L0-EB08_edna-transport`. Filenames do not change.
- An explicit `chunk_id: EB08` field is added to frontmatter as the citation alias.
- `kb_to_okf.py` builds and validates the `chunk_id → path` map, and fails on
  duplicate or missing chunk IDs. Chunk-ID citation continues to work unchanged.

`verified[]` also deserves a note: OKF's actor convention distinguishes `human:`,
`process:`, and `agent/version`. That is strictly better than the KB's single
`verified_by:` scalar, because the KB's audit loop mixes all three — a human
confirming a DOI, `kb_lib.py` stamping the ledger, and the model judging relevance
are different evidentiary weights and should not collapse into one field.

## What conformance buys

1. **A deterministic conformance gate.** `okf_validate.py --strict` plus the shipped
   GitHub Action turns drift into a failing build. The `edna-kb` skill currently warns
   in prose that "index topic lists can drift from chunk content, so grounding must
   come from the chunk body" — that warning becomes an enforced check.
2. **Retrieval that is not grep.** The toolchain ships a read-only MCP server exposing
   `search_concepts`, `read_concept`, and `get_neighbors`. `get_neighbors` walks
   markdown links and bundle-internal `sources` to return connected concepts — which is
   the Cross-Domain Query Routing Guide in `KB_INDEX.md`, derived from the graph
   instead of hand-maintained. The server writes nothing and resolves IDs only inside
   the bundle root.
3. **Attestation for computed results.** OKF v0.2's `type: Attested Computation`
   (`runtime`, `parameters`, `executor`, `attester`) is the right container for
   occupancy model runs, LOD/LOQ estimates, and RMT outputs — where the defensibility
   claim is about *how a number was produced*, not which paper it came from. The KB has
   no equivalent today.
4. **Portability.** The same bundle is readable by other agents and by `cat`.

## What conformance does NOT buy

OKF is a container format. It has no opinion on epistemics, so every one of these stays
the KB's own responsibility and must not be assumed handled:

- **find-then-validate.** OKF's `verified[]` records *that* a check occurred, not that a
  DOI resolved or that the paper is unretracted. The audit loop still owns that.
- **The relevance gate and the distant-field gate.** No OKF analogue.
- **TaxaFloc IP confidentiality.** OKF has `status` but no sensitivity classification;
  the public-disclosure rule stays in `edna-kb`.
- **Ledger dedupe memory.** OKF has no concept of "papers this chunk already rejected,"
  which is what makes the incremental audit converge under the Consensus 3-result cap.
- **Evidence pseudoreplication.** The independent-sources confidence rule (§15) is
  KB-specific reasoning over `sources[]`, not a format feature.

## Migration posture

Additive and reversible. Every OKF field above is *optional* under the spec — only
non-empty `type` is required for conformance. So the KB can adopt them incrementally,
chunk by chunk, during audits that are already touching frontmatter, with no flag day
and no renumbering. `kb_to_okf.py --check` reports conformance distance without writing.

## Spec-churn caveat

OKF went v0.1 → v0.2 in six weeks and v0.2 is where the trust fields live. Treat the
field names above as a moving target, pin the validator version in CI, and re-read the
spec before a bulk write. This is the main argument for the additive posture rather
than a one-shot conversion.
