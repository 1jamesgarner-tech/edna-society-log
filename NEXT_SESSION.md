# Continuation prompt — local session

Copy everything below the line into a new local Claude Code session started in a
directory where the eDNA KB folder is reachable.

---

## Context

I'm continuing work started in a Claude Code web session. That session ran in a remote
container with no access to my local files, so it could not reach the eDNA Knowledge
Base. You're running locally, so you can. Everything you need is below — assume you have
no prior conversation.

**Who/what:** I run the eDNA Knowledge Base — a validated, expert-curated store of
Layer 0 reference chunks and Layer 1 syntheses on eDNA science, New England
freshwater/marine systems, quantitative ecology (RMT, occupancy, EcoCASH, eDITH,
information theory), qPCR/ddPCR/CRISPR/metabarcoding, and the Bishir Monitoring
Solutions / TaxaFloc biosurveillance work. Two account-level skills operate it:
`edna-kb` (grounding protocol) and `edna-kb-audit` (incremental citation-enrichment
audit loop). The KB folder contains `KB_INDEX.md`, `L0/`, `L1/`,
`PROJECT_INSTRUCTIONS.md`, `PROJECT_MEMORY.md`, `scripts/kb_lib.py`,
`audit_ledger.json`, and `audit_runs/`.

**Goal:** build a Claude engineering system spanning (a) scientific writing and editing
and (b) business, management, capital recruitment, and entrepreneurship — comparable in
rigor to what the KB already does for eDNA science. The prior session surveyed and
evaluated what exists, then started on (a). (b) is deliberately still open.

## What already exists — do not re-derive this

Repo `1jamesgarner-tech/edna-society-log`, branch
`claude/claude-tools-business-science-8bimxf`. Clone or check out that branch. It is
otherwise a static GitHub Pages site (`index.html`, `.nojekyll`) — leave that alone.

    skills/README.md
    skills/edna-manuscript/SKILL.md                    domain overlay
    skills/edna-manuscript/references/okf-mapping.md   KB <-> OKF v0.2 crosswalk
    skills/edna-manuscript/scripts/kb_to_okf.py        read-only conformance reporter
    skills/edna-manuscript/tests/fixtures/kb_root/     synthetic KB (NOT the real one)

`edna-manuscript` is a thin domain overlay binding KB chunk-ID grounding to manuscript
writing/review. Its one real addition: no load-bearing scientific claim (parameter,
threshold, equation, detection limit, species assertion, defensibility statement) enters
prose unless it resolves to an exact supporting span in a validated chunk, or is marked
`[UNGROUNDED]`. It also carries independent-sources confidence checking (chunks
cross-cite, so three chunks echoing one reference is pseudoreplication, not three-source
support), distant-field applicability caveats, and TaxaFloc non-disclosure.

**Everything above is an untested prototype.** It was written against the *documented*
behavior of `edna-kb`/`edna-kb-audit` and never run against real chunks or a real
manuscript.

## Task 1 (do this first) — validate the crosswalk against the real KB

    python3 skills/edna-manuscript/scripts/kb_to_okf.py "<path to KB folder>" --json

Read-only, stdlib-only, never writes. The crosswalk it implements assumes KB chunk
frontmatter carries: `sources`, `topics`, `last_verified`, `verified_by`,
`review_after`, `sources_verified`, `revision_note`. Those were inferred from
`edna-kb-audit`'s text, not observed. Also assumed: chunk files are named
`L0/L0-<ID>_<slug>.md` and `L1/L1-<ID>_<slug>.md`.

If the real KB differs, correct `references/okf-mapping.md` and `kb_to_okf.py` to match
reality — reality wins, the document is the guess. Report what was wrong. Then tell me
the actual conformance distance: how many chunks already carry each field.

## Task 2 — decide on OKF conformance

**Open Knowledge Format** is an open, vendor-neutral spec from Google Cloud (v0.1
published 2026-06-12; v0.2 2026-07-25). It represents knowledge as a directory of
markdown files with YAML frontmatter cross-linked into a graph. v0.2 added the trust
signal families: provenance, trust, lifecycle, attestation. Only a non-empty `type`
field is required for conformance; everything else is optional, which is what makes
adoption additive.

Field families: **provenance** (`sources[]`, `author`, `usage_count`, `last_modified`,
`usage_window`) · **trust** (`generated: {by, at}`, `verified[]` with actor convention
`human:` / `process:` / `agent/version`) · **lifecycle** (`status`, `stale_after`) ·
**attestation** (`type: Attested Computation` plus `runtime`, `parameters`, `executor`,
`attester`).

The KB independently arrived at nearly this shape. Crosswalk: `sources:` → `sources[]`;
`last_verified:` + `verified_by:` → `verified[]`; `review_after:` → `stale_after`;
`revision_note:` → `log.md`; `topics:` → `tags`; L0/L1 → `type`.

**Toolchain:** https://github.com/scaccogatto/okf-skills (MIT, ~356 stars, 89 commits,
ships CI + tests + benchmark). Provides `/okf:okf`, `/okf:validate`, `/okf:backfill`,
`/okf:visualize`; `okf_validate.py` (deterministic conformance, `--strict`, `--json`,
`--migrate`); a composite GitHub Action; and a **read-only MCP server** exposing
`search_concepts`, `read_concept`, `get_neighbors`.

What conformance buys:
1. A deterministic validator plus CI gate. `edna-kb` currently only *warns in prose*
   that "index topic lists can drift from chunk content" — this makes drift a build
   failure.
2. Graph retrieval instead of grep. `get_neighbors` walks markdown links and
   bundle-internal `sources` — that is the Cross-Domain Query Routing Guide derived
   from the graph rather than hand-maintained in `KB_INDEX.md`.
3. `type: Attested Computation` as a container for occupancy runs, LOD/LOQ estimates,
   and RMT outputs, where defensibility is about how a number was produced. The KB has
   no equivalent today, and this is closest to the regulatory-grade thesis.

What it does NOT buy, and must not be assumed handled: find-then-validate (OKF's
`verified[]` records *that* a check happened, not that a DOI resolved or is
unretracted), the relevance gate, the distant-field gate, TaxaFloc IP confidentiality,
ledger dedupe memory, and the evidence-pseudoreplication rule. All stay KB-side.

**One structural friction:** OKF makes the file path the concept ID; the KB cites short
tokens (`EB08`, `S8`, `STAT-Occ01`) and `PROJECT_INSTRUCTIONS.md` §2 requires chunk-ID
citation. Resolution already chosen: keep filenames unchanged, OKF concept ID = path
minus `.md`, add `chunk_id:` frontmatter as the citation alias. Do not renumber
anything.

**Constraints:** migration must be additive and reversible — adopt fields chunk-by-chunk
during audits already touching frontmatter, no flag day. Pin the validator version in
CI: OKF went v0.1 → v0.2 in six weeks and the trust fields are new. Re-read the current
spec before any bulk write; treat the field names above as a moving target.

Before installing the toolchain, read its actual `SKILL.md` and validator source — not
just the README.

## Task 3 — the manuscript-integrity base

`edna-manuscript` is designed to compose onto a base that supplies lifecycle,
change-impact classes, claim-scope control, and release gates. Evaluation from the prior
session (based on reading actual `SKILL.md` files, not READMEs):

**Tier 1 — worth installing**

- **https://github.com/WenyuChiou/academic-writing-skills** (MIT, ~27 stars, 66 commits,
  has `evals/` and `tests/`). Two skills: `academic-writing-skills` (15KB) and
  `paper-review` (9KB), both dispatching to a `references/` tree. Real substance:
  integrity gates (authority, claim scope, version integrity, release integrity);
  deterministic audit scripts (`audit_manuscript_state.py`, `audit_text_consistency.py`,
  `audit_prose_patterns.py`, `audit_candidate_text.py`, `audit_docx_structure.py`,
  `run_regression_tests.py`); explicit rule "never invent results, mechanisms,
  citations, metadata, analyses, or field requirements"; and an `overlay-contract.md`
  defining how to compose a domain skill without promoting domain rules into universal
  ones. `paper-review` ships a `water-cnhs-uncertainty.md` module (water resources,
  coupled natural-human systems, equifinality) and a flood/hydrodynamics module.
  **CAVEAT: its README install command points at `WenyuChiou/ai-research-skills`, a
  different repo than the skill source. Resolve that before installing.**
- **https://github.com/neuromechanist/research-skills** (BSD-3, 45 stars, Zenodo DOI
  10.5281/zenodo.20696515, cross-agent). Eight plugins. Relevant: `opencite`
  (Semantic Scholar / OpenAlex / PubMed / arXiv / bioRxiv), `manuscript`
  (citation-traceable lit review, peer review, journal formatting), and `grant`
  (NIH/NSF **and SBIR/STTR** — non-dilutive capital for Bishir, so it bridges into the
  business half below).

**Tier 2 — useful, narrower**

- https://github.com/andrehuang/academic-writing-agents (MIT, 183 stars). 12-agent
  orchestrator; real `bibliography-auditor` (bib completeness, arXiv version updates,
  venue consistency) and `paper-crawler` (DBLP + OpenAlex). LaTeX/`.tex`-centric,
  auto-triggers on file type, 30 writing principles in one flat file.
- https://github.com/JeanDiable/academic-research-plugin (MIT, 20 stars). Worth
  stealing: `citation-assistant` uses `bibtex_utils.py` with a Semantic Scholar → DBLP →
  arXiv fallback chain that only fetches from official sources and never fabricates.
  ML-conference-shaped otherwise.

**Skip**

- https://github.com/chenlu-hung/scientific-writing — 0 stars, 3 commits, no license,
  README install URL points at a nonexistent repo. Its 3-reviewer + area-editor
  peer-review simulation is a good pattern to reimplement, not to depend on.
- https://github.com/K-Dense-AI/claude-scientific-writer — 2.3k stars and the most
  polished, but requires a paid `PARALLEL_API_KEY` and routes literature search through
  a third party. Given TaxaFloc confidentiality that is an outbound-data question, not
  just a cost one.

## Task 4 — the set-aside goals: business, management, capital recruitment, entrepreneurship

Deliberately deferred to do scientific writing first. Nothing here has been evaluated by
reading source — treat the list as candidates, and apply the same evaluate-before-install
discipline used above.

**First-party, already in my claude.ai plugin catalog (`knowledge-work-plugins`
marketplace), all currently disabled** — these are curated, unlike the GitHub repos:

- `carta-crm` — investors, companies, contacts, deals, notes, **fundraisings**;
  deal-flow analytics, "prepare for meeting", "get angles". Closest to a real
  capital-recruitment system.
- `finance` — journal entries, reconciliation, financial statements, variance analysis,
  close management, audit/SOX.
- `small-business` — ~30 skills: cash-flow snapshot, margin analyzer, payroll planning,
  contract review, CRM cleanup, campaigns, tax prep; wired to QuickBooks/Stripe/HubSpot/
  Square/Docusign/Canva.
- `bigdata-com` — investment memos, peer comparables, valuation snapshots, pre/post-IPO
  analysis, thematic research.
- `product-management`, `design`, `common-room`, `customer-support`, `tavily`.
- `bio-research` — scientific problem selection plus PubMed / bioRxiv / Consensus /
  Wiley / ChEMBL MCP servers. Overlaps the literature stack `edna-kb-audit` already uses.

**Community candidates (unvetted):**
https://github.com/tjboudreaux/cc-skills-vc-fundraising (pitch analysis, fundraising
strategy, investor relations; Sequoia/a16z/Benchmark/YC first principles) ·
https://github.com/dkorobtsov/pitch-deck (narrative-first, phased gates, anti-BS
enforcement) · https://github.com/Stevekaplanai/pitch-deck-mastery-skill ·
https://github.com/Overdrive-Consulting/vc-fundraising-skill ·
https://github.com/alirezarezvani/claude-skills (380+ skills, 28 C-level advisory).
Aggregators: https://github.com/rohitg00/awesome-claude-code-toolkit ·
https://github.com/ComposioHQ/awesome-claude-skills · https://claudemarketplaces.com/

**Open design question I want your view on:** the fundraising and business skills are
prompt scaffolding with no validated corpus underneath — which matters less for a pitch
deck than for a manuscript, but Bishir/TaxaFloc investor materials make factual claims
about methods, performance, and market that *should* be grounded. Does the
`edna-manuscript` grounding-gate pattern (claims resolve to chunk spans or get marked
`[UNGROUNDED]`) transfer to a `bishir-investor` overlay drawing on the same KB? Or does
that need a separate commercial KB with different validation rules?

## Housekeeping

- These MCP servers need authorization before their tools work — do via claude.ai
  connector settings: **BioRender, Owkin, Synapse_org**.
- Nothing has been installed. No KB content has been modified. No PR opened.
- Commits on the branch above end with a `Co-Authored-By: Claude Opus 5` trailer.

## How I like to work

- Ask clarifying questions before diving into complex topics.
- Evaluate before installing: read the actual `SKILL.md` and scripts, not the README.
- Be explicit about what was tested versus assumed. The prior session's prototype is
  labeled untested for a reason — keep that honesty.
- Never invent citations. Find-then-validate, web-verified DOIs only.
- Never expose TaxaFloc device architecture (solid-phase La3+ capture, radial flow,
  EDTA elution) in anything public-facing, including manuscripts, preprints, grant
  narratives, and investor materials.

## Start here

Confirm you can see the KB folder, then run Task 1 and report what the crosswalk got
wrong before changing anything else.
