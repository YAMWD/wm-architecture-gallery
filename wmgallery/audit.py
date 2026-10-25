"""Check that every published architecture has a current, reproducible source review.

This checks provenance, coverage, routing and generated-file consistency. It does
not infer scientific correctness from matching words or from a source-basis tag.
The paper/code comparison and its limitations are recorded in the review ledger.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

from . import registry as R


LEDGER = Path(R.ROOT) / "docs" / "architecture_audit.json"


def fingerprint(model):
    """Bind a review to the card and figure, excluding historical audit counters."""
    payload = {k: v for k, v in model.items()
               if not k.startswith("_") and k not in ("audit", "source_review")}
    data = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def load_reviews(models=None, path=LEDGER):
    models = R.load_models() if models is None else models
    ledger = json.loads(Path(path).read_text(encoding="utf-8"))
    reviews = ledger["models"]
    expected = {m["slug"] for m in models}
    if set(reviews) != expected:
        raise ValueError("review/model coverage differs: %s" % sorted(set(reviews) ^ expected))
    for model in models:
        slug = model["slug"]
        review = reviews[slug]
        errors = R.validate(model)
        if errors:
            raise ValueError("%s: %s" % (slug, "; ".join(errors)))
        if "diagram" in model:
            raise ValueError("%s: an unchecked duplicate diagram is still present" % slug)
        if review["model_sha256"] != fingerprint(model):
            raise ValueError("%s: card changed since its source review; review the change first" % slug)
        if review["variant"] != model.get("figure_variant"):
            raise ValueError("%s: figure and review configurations differ" % slug)
        if not all(review.get(k) for k in ("variant", "architecture", "references", "checked")):
            raise ValueError("%s: incomplete source review" % slug)
        if not any(ref["kind"] in ("paper", "report", "official page") for ref in review["references"]):
            raise ValueError("%s: missing original publication" % slug)
        has_code = any(ref["kind"] == "code" for ref in review["references"])
        if not has_code and not review.get("limitations"):
            raise ValueError("%s: missing-code limitation must be explicit" % slug)
        for ref in review["references"]:
            if not re.fullmatch(r"[0-9a-f]{64}", ref.get("sha256", "")) or not ref.get("cached_as"):
                raise ValueError("%s: source needs its hash and cached filename" % slug)
            if ref["kind"] in ("code", "checkpoint metadata") and not re.fullmatch(r"[0-9a-f]{40}", ref.get("revision", "")):
                raise ValueError("%s: unpinned code reference" % slug)
    return ledger


def check_sources(ledger, cache):
    checked = set()
    for review in ledger["models"].values():
        for ref in review["references"]:
            key = ref["cached_as"], ref["sha256"]
            if key in checked:
                continue
            path = cache / ref["cached_as"]
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != ref["sha256"]:
                raise ValueError("source bytes differ: %s" % path)
            checked.add(key)
    return len(checked)


def check_artifacts(models, ledger=None):
    from . import stack as S
    ledger = load_reviews(models) if ledger is None else ledger
    root = Path(R.ROOT) / "docs"
    count = 0
    for model in models:
        for directory, options in (("stack", {}), ("mini", {"mini": True}),
                                   ("stack_mini", {"mini": True}),
                                   ("stack_condensed", {"condensed": True})):
            svg, warnings, _ = S.render_stack_svg(model, **options)
            if warnings:
                raise ValueError("%s/%s: %s" % (directory, model["slug"], "; ".join(warnings)))
            path = root / "svg" / directory / (model["slug"] + ".svg")
            if path.read_text(encoding="utf-8") != svg:
                raise ValueError("stale generated figure: %s" % path)
            count += 1
    published = json.loads((root / "data.json").read_text(encoding="utf-8"))
    if {m["slug"] for m in published} != {m["slug"] for m in models}:
        raise ValueError("published model coverage differs")
    for model in published:
        if fingerprint(model) != fingerprint(next(m for m in models if m["slug"] == model["slug"])):
            raise ValueError("stale published data: %s" % model["slug"])
        review = dict(ledger["models"][model["slug"]], date=ledger["date"])
        if model.get("source_review") != review:
            raise ValueError("stale published source review: %s" % model["slug"])
    return count


def write_report(ledger, path):
    reviews = ledger["models"]
    code_count = sum(any(r["kind"] == "code" for r in m["references"]) for m in reviews.values())
    lines = ["# Architecture source review — " + ledger["date"], "",
             "All %d gallery models were compared with their original publication or official technical page. "
             "Released implementation files were also checked for %d models. For the remaining %d, no matching "
             "public implementation was found in the consulted sources; their figures show only disclosed details."
             % (len(reviews), code_count, len(reviews) - code_count), "",
             "The figures are operator-level schematics of the named configuration below. They are not claims that "
             "every model variant, training path, or hardware optimization has the same graph. A module box can "
             "encapsulate projections and normalization; an expanded residual shows the actual skip boundary. "
             "Performance numbers are source reports or labelled arithmetic, not new measurements.", "",
             "This review corrects the previous audit rather than inheriting its verification labels. "
             "Paper/code disagreements and unavailable details are retained as limitations. No architecture is "
             "filled in from a related model or a conventional transformer layout.", "",
             "## Corrections that affect interpretation", ""]
    lines += ["- " + item for item in ledger["common_findings"]]
    lines += ["", "## Coverage", "", "| Model | Figure configuration | Sources |",
              "|---|---|---|"]
    for slug, review in reviews.items():
        source = "Publication + released code" if any(r["kind"] == "code" for r in review["references"]) else review["coverage"]
        lines.append("| [%s](#%s) | %s | %s |" % (review["name"], slug.replace("_", "-"), review["variant"], source))
    lines += ["", "## Per-model findings", ""]
    for slug, review in reviews.items():
        lines += ["### " + slug.replace("_", "-"), "", "**%s — %s.** %s" %
                  (review["name"], review["variant"], review["architecture"]), "",
                  "Checked: " + "; ".join(review["checked"]) + ".", ""]
        if review["changes"]:
            lines += ["Corrections: " + " ".join(review["changes"]), ""]
        if review["limitations"]:
            lines += ["Limits / differences: " + " ".join(review["limitations"]), ""]
        for ref in review["references"]:
            label = ref.get("label") or ref.get("path") or ref["kind"]
            lines.append("- [%s](%s)%s" % (label, ref.get("view_url", ref["url"]),
                         (" — revision `" + ref["revision"] + "`") if ref.get("revision") else ""))
        lines.append("")
    lines += ["## Reproduce the integrity checks", "", "```bash", "python3 -m wmgallery.audit",
              "python3 -m wmgallery.audit --sources '" + ledger["source_cache"] + "'",
              "python3 -m wmgallery.audit --artifacts", "```", "",
              "The JSON ledger records SHA-256 hashes of the reviewed card and every downloaded primary source. "
              "The checks detect stale cards, missing reviews, invalid feedback ports, source-byte changes, and stale "
              "SVG/data exports. They do not prove scientific correctness by searching for names in code. "
              "No downloaded model code or weights were executed.", ""]
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, help="also verify the downloaded primary-source bytes")
    parser.add_argument("--artifacts", action="store_true", help="also compare all four SVG exports and data.json")
    parser.add_argument("--write-report", action="store_true", help="regenerate architecture_audit.md from the ledger")
    args = parser.parse_args(argv)
    models = R.load_models()
    ledger = load_reviews(models)
    print("PASS: %d/%d model source reviews current; flow schemas and feedback ports valid" % (len(models), len(models)))
    if args.sources:
        print("PASS: %d original source files match their recorded hashes" % check_sources(ledger, args.sources))
    if args.artifacts:
        print("PASS: %d generated SVGs and published data match the reviewed cards" % check_artifacts(models, ledger))
    if args.write_report:
        write_report(ledger, LEDGER.with_suffix(".md"))


if __name__ == "__main__":
    main()
