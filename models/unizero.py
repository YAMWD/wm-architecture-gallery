MODEL = {
    "slug": "unizero",
    "name": "UniZero",
    "year": 2024, "month": 6,
    "org": "Shanghai AI Laboratory",
    "family": "rl",
    "role": "Per-step latent model",
    "status": "TMLR 2025",
    "params": "size not disclosed",
    "params_num": None,
    "open": "code",
    "links": {"arXiv": "https://arxiv.org/abs/2406.10667", "code": "https://github.com/opendilab/LightZero"},
    "summary": "Plans with MuZero's MCTS over a 2-layer transformer backbone that reads two tokens per step, latent "
               "and action. A conv encoder maps each observation to a 768-d SimNorm latent with no decoder, and the "
               "transformer output feeds heads for the next latent, reward, policy and value. Every real action runs "
               "50 MCTS simulations, each two dependent single-token transformer passes (action, then predicted latent) "
               "against a KV cache of the last 4 steps, so inference is, on our reading, a small-batch, latency-bound loop rather than a FLOP-bound one.",
    "tagline": "MuZero-style MCTS on a tiny transformer",
    "facts": [
        ("Representation", "Conv encoder → one 768-d latent per step with SimNorm (simplex groups of 8); 64x64 Atari frames; no reconstruction"),
        ("Core", "2 transformer layers, d 768, 8 heads, GELU, dropout 0.1 (Atari, DMC); d 64 and 4 heads for the long-term memory tasks. "
                 "The figure follows the released code: pre-norm, final LayerNorm and FFN width 4D = 3072. "
                 "Table 6 instead specifies post-norm and FFN width D; parameter count not listed"),
        ("Attention", "Causal over interleaved (latent, action) tokens; training context H = 10 steps = 20 tokens; inference context H_infer = 4 steps (memory_length + 16 on long-term tasks)"),
        ("Actions", "A learned action-embedding token per step (lookup table for discrete actions; for continuous ones a linear layer per App. B.2 and the code, a 2-layer MLP per Sec. 3.2.1)"),
        ("Prediction", "Two dependent single-token passes per imagined step (code): the action token yields the next latent (SimNorm) and reward, the predicted latent fed back as a token yields policy and value"),
        ("Decoder", "None: no reconstruction loss; a decode-regularization ablation did not help"),
        ("Memory", "KV cache over the last H_infer = 4 steps = 8 tokens [D], reused by every node of the search tree"),
        ("Speed", "Atari 100k agent trained in ~4 h on one A100 80GB, 1M VisualMatch steps in ~30 h (authors); no inference latency reported"),
        ("Key detail", "50 MCTS simulations per real step = 100 dependent single-token transformer passes [D] (2 per simulation in the code) on a cache of at most 8 tokens: a latency-bound inner loop (our reading)"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2406.10667 Sec. 3.2-3.3 (tokens, KV cache, MCTS), App. B Tables 6-8 (architecture, hyperparameters), App. B.5 (compute)",
                "LightZero code (v0.1.0, v0.2.0): lzero/model/unizero_world_models/world_model.py, transformer.py; zoo/atari/config/atari_unizero_config.py",
                "LightZero README (TMLR 2025 acceptance)"],
    "figure_variant": "Released 2x768 pre-norm transformer with final LayerNorm",
    "flow": {
        "below": [{"text": "Frame 64×64 + action"}],
        "stack": [
            {"box": "Conv encoder", "id": "enc", "style": "teal", "basis": "stated"},
            {"box": "SimNorm latent z", "id": "lat", "basis": "stated"},
            {"box": "Interleave (z, a) tokens", "short": "Interleave z, a", "id": "seq", "side": "Action emb.", "basis": "stated", "side_basis": "stated"},
            {"box": "Add learned positions", "id": "pos", "minor": True, "basis": "stated"},
            {"group": [
                {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"},
                              {"box": "Masked self-attention", "id": "attn", "style": "dark", "basis": "code"}]},
                {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"},
                              {"box": "Feed forward", "id": "ffn", "basis": "code"}]},
            ], "repeat": "2 ×", "id": "block"},
            {"box": "Final LayerNorm", "minor": True, "basis": "code"},
            {"fanout": [[{"box": "Policy + value head", "id": "pol", "terminal": True, "minor": True, "basis": "stated"}],
                        [{"box": "Dynamics head (MLP)", "short": "Dynamics head", "id": "dyn", "minor": True, "basis": "stated"}, {"box": "Next latent + reward", "id": "next", "basis": "stated"}]]},
        ],
        "above": [{"text": "Next latent → MCTS, no decoding"}],
        "insets": [{"for": "ffn", "stack": [{"box": "Linear 768 → 3072", "basis": "code"}, {"box": "GELU (tanh)", "basis": "code"}, {"box": "Linear 3072 → 768", "basis": "code"}]},
                   {"for": "dyn", "label": "MCTS per real step", "stack": [{"box": "Pick an action (UCB)", "basis": "stated"}, {"box": "Two 1-token passes", "basis": "code"},
                                                                          {"box": "Back up the value, ×50", "basis": "stated"}]}],
        "annotations": [
            {"at": "lat", "text": "SimNorm in groups of *8*", "side": "left"},
            {"at": "seq", "text": "*2* tokens per step · context of *10* steps", "side": "left", "key": True},
            {"at": "attn", "text": "*8* heads · KV of *4* steps", "side": "left", "key": True},
            {"at": "next", "text": "*50* MCTS calls per action", "side": "left", "key": True},
            {"at": "block", "text": "*2* layers · width *768*", "side": "right", "key": True},
        ],
        "feedback": "predicted z",
        "feedback_from": "next",
        "feedback_to": "seq",
    },
}
