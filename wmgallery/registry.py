"""Load model specs from models/*.py (each file defines MODEL = {...}) and validate them."""
import os
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MODELS_DIR = os.path.join(ROOT, "models")

FAMILIES = {
    "rl": "RL world models (small, latent)",
    "token": "Discrete-token video models",
    "dit": "Causal diffusion transformers (interactive video)",
    "driving": "Driving and robot video world models",
    "jepa": "Embedding predictors (JEPA-style)",
    "wam": "World-action models",
    "llm": "LLM and code world models",
    "object": "Object-centric world models",
    "ssm": "State-space and hybrid designs",
}
ROLES = ["Discrete-token model", "Per-step latent model", "Diffusion transformer", "Embedding predictor",
         "LLM or mixture of transformers", "Object-centric model", "SSM hybrid"]
EVIDENCE = {"read": "read from the primary publication and available code",
            "claim": "developer claim only"}
REQUIRED = ["slug", "name", "year", "org", "family", "role", "status", "params", "summary", "facts", "evidence",
            "sources", "flow", "figure_variant"]


def load_models(models_dir=MODELS_DIR, only=None):
    specs = []
    for fn in sorted(os.listdir(models_dir)):
        if not fn.endswith(".py") or fn.startswith("_"):
            continue
        slug = fn[:-3]
        if only and slug not in only:
            continue
        path = os.path.join(models_dir, fn)
        sp = importlib.util.spec_from_file_location("wm_model_" + slug, path)
        mod = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(mod)
        m = dict(mod.MODEL)
        m.setdefault("slug", slug)
        if m["slug"] != slug:
            raise ValueError("%s: slug %r must match the file name" % (fn, m["slug"]))
        m["_file"] = path
        specs.append(m)
    return specs


def validate(m):
    errs = []
    for k in REQUIRED:
        if k not in m:
            errs.append("missing key %r" % k)
    if errs:
        return errs
    if m["family"] not in FAMILIES:
        errs.append("unknown family %r" % m["family"])
    if m["role"] not in ROLES:
        errs.append("unknown role %r (use one of %s)" % (m["role"], ROLES))
    if m["evidence"] not in EVIDENCE:
        errs.append("evidence must be one of %s" % list(EVIDENCE))
    if "diagram" in m:
        errs.append("legacy diagram is unsupported; use one source-reviewed flow")
    for f in m["facts"]:
        if not (isinstance(f, (list, tuple)) and len(f) == 2):
            errs.append("facts must be (label, text) pairs")
            break
    flow = m["flow"]
    ids = set()

    def check_nodes(nodes):
        for node in nodes:
            if node.get("id"):
                if node["id"] in ids:
                    errs.append("duplicate flow id %r" % node["id"])
                ids.add(node["id"])
            if "box" in node and node.get("basis") not in ("stated", "code"):
                errs.append("box %r needs a stated or code source basis" % node["box"])
            if "side" in node and node.get("side_basis") not in ("stated", "code"):
                errs.append("side input %r needs a stated or code source basis" % node["side"])
            for key in ("group", "residual"):
                check_nodes(node.get(key, []))
            for branch in node.get("fanout", []):
                check_nodes(branch)

    for key in ("below", "stack", "above"):
        check_nodes(flow.get(key, []))
    if not flow.get("stack"):
        errs.append("flow needs a nonempty stack")
    for annotation in flow.get("annotations", []):
        if annotation.get("at") not in ids:
            errs.append("annotation target %r is missing" % annotation.get("at"))
    for inset in flow.get("insets", []):
        if inset.get("for") not in ids:
            errs.append("inset target %r is missing" % inset.get("for"))
        # Insets have their own local ids; only the main diagram's ids are
        # eligible feedback endpoints and annotation targets.
        outer_ids = ids.copy()
        check_nodes(inset.get("stack", []))
        ids.clear()
        ids.update(outer_ids)
    if flow.get("feedback"):
        for key in ("feedback_from", "feedback_to"):
            if flow.get(key) not in ids:
                errs.append("%s must name an existing tensor port" % key)
    return errs


def sort_key(m):
    return (m.get("year", 0), m.get("month", 0), m["name"].lower())
