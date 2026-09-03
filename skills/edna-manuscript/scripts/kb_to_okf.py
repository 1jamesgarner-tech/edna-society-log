#!/usr/bin/env python3
"""Report how far an eDNA KB folder is from OKF v0.2 conformance.

Read-only by design: this never writes to the KB. It parses L0/L1 chunk frontmatter,
builds the chunk_id -> path map that OKF's path-as-ID model needs, and reports which
OKF trust/provenance/lifecycle fields each chunk already satisfies via its existing
KB fields.

Usage:
    python3 kb_to_okf.py <kb_root>            # human-readable report
    python3 kb_to_okf.py <kb_root> --json     # machine-readable
    python3 kb_to_okf.py <kb_root> --emit ID  # proposed frontmatter for one chunk, to stdout

See ../references/okf-mapping.md for the crosswalk this implements.
"""

import argparse
import json
import os
import re
import sys

# KB field -> (OKF field, family). Mirrors the crosswalk table in okf-mapping.md.
CROSSWALK = {
    "sources": ("sources", "provenance"),
    "last_verified": ("verified", "trust"),
    "verified_by": ("verified", "trust"),
    "review_after": ("stale_after", "lifecycle"),
    "topics": ("tags", "descriptive"),
}
# OKF requires exactly one field for conformance: a non-empty `type`.
OKF_REQUIRED = ["type"]

CHUNK_FILE = re.compile(r"^L(?P<layer>[01])-(?P<chunk_id>[A-Za-z0-9][A-Za-z0-9-]*?)_(?P<slug>.+)\.md$")


def parse_frontmatter(text):
    """Minimal YAML-subset parser: scalars and '- ' block lists. Returns {} if absent.

    Deliberately not PyYAML — the KB may be read on a machine without it, and the
    subset used in chunk frontmatter is small and regular.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    body = text[text.find("\n", 3) + 1 : end]
    fields, key = {}, None
    for raw in body.split("\n"):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith(("  - ", "- ")) and key:
            fields.setdefault(key, [])
            if isinstance(fields[key], list):
                fields[key].append(raw.split("- ", 1)[1].strip())
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", raw)
        if m:
            key, value = m.group(1), m.group(2).strip()
            fields[key] = value if value else []
    return fields


def scan(kb_root):
    chunks, problems = [], []
    for layer in ("L0", "L1"):
        d = os.path.join(kb_root, layer)
        if not os.path.isdir(d):
            problems.append(f"missing layer directory: {layer}/")
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".md"):
                continue
            m = CHUNK_FILE.match(name)
            rel = f"{layer}/{name}"
            if not m:
                problems.append(f"filename does not encode a chunk ID: {rel}")
                continue
            with open(os.path.join(d, name), encoding="utf-8") as fh:
                fm = parse_frontmatter(fh.read())
            chunks.append(
                {
                    "chunk_id": m.group("chunk_id"),
                    "path": rel,
                    "okf_id": rel[:-3],  # OKF concept ID is the path minus .md
                    "layer": layer,
                    "present": sorted(k for k in CROSSWALK if fm.get(k)),
                    "missing": sorted(k for k in CROSSWALK if not fm.get(k)),
                    "has_okf_type": bool(fm.get("type")),
                    "source_count": len(fm["sources"]) if isinstance(fm.get("sources"), list) else 0,
                }
            )

    seen = {}
    for c in chunks:
        seen.setdefault(c["chunk_id"], []).append(c["path"])
    for cid, paths in sorted(seen.items()):
        if len(paths) > 1:
            problems.append(f"duplicate chunk ID {cid}: {', '.join(paths)}")

    return chunks, problems


def emit(chunk):
    """Proposed additive OKF frontmatter for one chunk. Printed, never written."""
    lines = [
        f"type: {'L0 Reference Chunk' if chunk['layer'] == 'L0' else 'L1 Synthesis'}",
        f"chunk_id: {chunk['chunk_id']}   # citation alias; OKF concept ID is {chunk['okf_id']}",
    ]
    if "review_after" in chunk["missing"]:
        lines.append("stale_after: <date>   # from review_after, set by volatility")
    if "last_verified" in chunk["missing"]:
        lines.append("verified: []   # OKF actors: human:<who> / process:kb_lib / agent/<model>")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kb_root", help="folder containing KB_INDEX.md, L0/ and L1/")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--emit", metavar="CHUNK_ID", help="print proposed frontmatter for one chunk")
    args = ap.parse_args()

    if not os.path.isfile(os.path.join(args.kb_root, "KB_INDEX.md")):
        sys.exit(f"not a KB root (no KB_INDEX.md): {args.kb_root}")

    chunks, problems = scan(args.kb_root)

    if args.emit:
        match = [c for c in chunks if c["chunk_id"] == args.emit]
        if not match:
            sys.exit(f"no chunk with ID {args.emit}")
        print(emit(match[0]))
        return 0

    conformant = [c for c in chunks if c["has_okf_type"]]
    if args.json:
        print(json.dumps({"chunks": chunks, "problems": problems,
                          "okf_conformant": len(conformant), "total": len(chunks)}, indent=2))
        return 1 if problems else 0

    print(f"KB root: {args.kb_root}")
    print(f"chunks: {len(chunks)}  ({sum(c['layer'] == 'L0' for c in chunks)} L0, "
          f"{sum(c['layer'] == 'L1' for c in chunks)} L1)")
    print(f"OKF-conformant today (non-empty `type`): {len(conformant)}/{len(chunks)}")
    print("\nfield coverage against the crosswalk:")
    for kb_field, (okf_field, family) in sorted(CROSSWALK.items()):
        n = sum(1 for c in chunks if kb_field in c["present"])
        print(f"  {kb_field:<16} -> {okf_field:<12} [{family:<11}] {n}/{len(chunks)}")
    if problems:
        print("\nproblems:")
        for p in problems:
            print(f"  - {p}")
    print("\nNothing was written. See references/okf-mapping.md for what conformance buys.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
