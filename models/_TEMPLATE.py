# Copy to models/<slug>.py. Replace every placeholder with evidence from the
# original publication and official code. This is not a default transformer.
# Expand the core only where the sources disclose its actual operations.
# Read docs/SPEC.md and docs/FLOW.md; add a source review before site publication.
MODEL = {
    "slug": "template",
    "name": "Model name",
    "year": 2025,
    "month": 1,
    "org": "Organization",
    "family": "rl",
    "role": "Per-step latent model",
    "status": "Publication status",
    "params": "not disclosed",
    "params_num": None,
    "open": "closed",
    "links": {},
    "tagline": "Replace with a sourced description",
    "summary": "Identify the model and the exact configuration drawn.",
    "figure_variant": "Replace with the exact sourced configuration",
    "facts": [
        ("Representation", "Describe the sourced representation and dimensions."),
        ("Core", "Describe only disclosed operators, ordering and dimensions."),
        ("Attention", "Identify the actual mask and context, if disclosed."),
        ("Actions", "Locate conditioning in the actual data path."),
        ("Prediction", "Name the released sampler and its repetitions, if known."),
        ("Decoder", "Describe the output role without assuming pixels."),
        ("Memory", "State the disclosed cache/state policy or mark unknown."),
        ("Speed", "Cite variant and hardware, or state undisclosed."),
        ("Key detail", "Record important paper/code differences."),
    ],
    "evidence": "read",
    "sources": ["Replace with original publication sections and pinned code files"],
    "flow": {
        "below": [{"text": "Disclosed model input"}],
        "stack": [
            {"box": "Disclosed model core", "id": "core", "basis": "stated"},
        ],
        "above": [{"text": "Disclosed model output"}],
        "annotations": [],
    },
}
