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
EVIDENCE = {"verified": "adversarially verified (3-vote)", "read": "read from the primary source",
            "claim": "developer claim only"}
REQUIRED = ["slug", "name", "year", "org", "family", "role", "status", "params", "summary", "facts", "evidence",
            "sources", "diagram"]
TOKEN_KINDS = {"frame", "latent", "action", "reward", "state", "text", "register", "slot", "noise", "audio"}
ROW_KINDS = {"attn", "xattn", "mlp", "action", "ssm", "moe", "note"}
SAMPLING_KINDS = {"ar", "parallel", "diffusion", "regress", "search"}


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
    d = m["diagram"]
    for g in d.get("tokens", {}).get("groups", []):
        if g[0] not in TOKEN_KINDS:
            errs.append("token kind %r unknown" % g[0])
    for r in d.get("core", {}).get("rows", []):
        if r[0] not in ROW_KINDS:
            errs.append("core row kind %r unknown" % r[0])
    s = d.get("sampling", {})
    if s and s.get("kind", "regress") not in SAMPLING_KINDS:
        errs.append("sampling kind %r unknown" % s.get("kind"))
    for f in m["facts"]:
        if not (isinstance(f, (list, tuple)) and len(f) == 2):
            errs.append("facts must be (label, text) pairs")
            break
    return errs


def sort_key(m):
    return (m.get("year", 0), m.get("month", 0), m["name"].lower())
