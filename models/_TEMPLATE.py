# Copy this file to models/<slug>.py and fill it in. Keep every number traceable to a source listed in
# "sources"; mark your own arithmetic with [D] in the text. Run:  python3 -m wmgallery.render <slug>
# and look at site/png/<slug>.png before committing.
MODEL = {
    "slug": "template",                 # must equal the file name without .py
    "name": "Model name",
    "year": 2025, "month": 6,           # first public release (arXiv v1 or announcement)
    "org": "Organisation",
    "family": "dit",                    # rl | token | dit | driving | jepa | wam | llm | object | ssm
    "role": "Diffusion transformer",    # Discrete-token model | Per-step latent model | Diffusion transformer |
                                        # Embedding predictor | LLM or mixture of transformers |
                                        # Object-centric model | SSM hybrid
    "status": "arXiv preprint",         # venue, or 'company report', 'blog post', ...
    "params": "1.3B",                   # core model size as a short string
    "params_num": 1.3e9,                # number for sorting (None if unknown)
    "open": "code + weights",           # 'code + weights' | 'code' | 'closed' | 'weights'
    "links": {"arXiv": "https://arxiv.org/abs/XXXX.XXXXX", "code": "https://github.com/..."},
    "summary": "Two or three sentences: what the model is, what the transformer does inside it, and why it matters.",
    "facts": [
        ("Representation", "what one frame becomes (tokens, latents, embedding)"),
        ("Core", "layers, width, heads; base model if any"),
        ("Attention", "causal / block-causal / factorized; context length"),
        ("Actions", "how actions enter"),
        ("Prediction", "next-token / MaskGIT / diffusion steps / regression; passes per frame"),
        ("Decoder", "what produces pixels, or 'none'"),
        ("Memory", "KV window, retrieval, SSM state"),
        ("Speed", "reported speed, resolution, hardware (say whose claim)"),
        ("Key detail", "the one thing to remember"),
    ],
    "evidence": "read",                 # verified | read | claim
    "sources": ["arXiv XXXX.XXXXX Sec. 3", "GitHub config"],
    "diagram": {
        "encoder": {"text": "Frame -> 3D causal VAE", "sub": "880 latents per frame", "tag": "frozen"},
        "tokens": {"groups": [("latent", 20, "2,640 latents per chunk"), ("action", 2, "actions")],
                   "note": "window 6 latent frames = 5,280 tokens"},
        "core": {"title": "DiT x30 · d 1536 · 12 heads",
                 "rows": [("attn", "Block-causal self-attention"),
                          ("action", "Action modules in blocks 1-15"),
                          ("mlp", "MLP")],
                 "notes": ["rolling KV cache, 6 latent frames"]},
        "sampling": {"kind": "diffusion", "text": "DMD-distilled flow, 3 steps", "sub": "per 12-frame chunk"},
        # "heads": ["reward", "value"],
        "decoder": {"text": "VAE decoder -> 12 frames", "sub": "352x640", "tag": "frozen"},
        "loop": "AR rollout",
    },
}
