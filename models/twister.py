MODEL = {
    "slug": "twister",
    "name": "TWISTER",
    "year": 2025, "month": 3,
    "org": "University of Würzburg",
    "family": "rl",
    "role": "Per-step latent model",
    "status": "ICLR 2025",
    "params": "~8-9M transformer",
    "params_num": 8.5e6,
    "open": "code",
    "links": {"arXiv": "https://arxiv.org/abs/2503.04416", "code": "https://github.com/burchim/TWISTER"},
    "summary": "DreamerV3 with its GRU replaced by a small Transformer State-Space Model and an extra action-conditioned "
               "contrastive objective. A CNN VAE encodes 64x64 frames as 32x32 categoricals, an action mixer fuses state "
               "and action into one token, and a 4-block causal transformer with Transformer-XL relative positions "
               "predicts the next state, reward and continuation. The cache is capped at 8 steps, so per-step memory is "
               "bounded. The score gain comes from AC-CPC, which predicts features 10 steps ahead given the future "
               "actions, not from the transformer swap.",
    "facts": [
        ("Representation", "32 categoricals x 32 classes per 64x64 RGB frame from a CNN VAE (4 strided conv layers)"),
        ("Core", "TSSM: 4 blocks, d 512, 8 heads, FFN 1024, dropout 0.1; ~8-9M transformer parameters (repo preset estimate)"),
        ("Attention", "Causal self-attention with Transformer-XL relative positions; attention context 8 steps; training sequences T = 64, batch 16"),
        ("Actions", "Action mixer (Linear + LN + SiLU to 512) fuses the flattened 32x32 state with the one-hot action into one token"),
        ("Prediction", "One pass per imagined step; a dynamics-predictor MLP samples the next categorical state from h_t; imagination horizon 15"),
        ("Decoder", "CNN decoder reconstructs from z_t for training only; the actor-critic uses s_t = {h_t, z_t}, so nothing is decoded in imagination"),
        ("Memory", "Hidden states of the previous segment are cached and reused as context; the released code caps the cache at 8 steps (att_context_left = 8)"),
        ("Speed", "No inference or wall-clock figure in the paper; Atari 100k mean/median HNS 162/77 (authors)"),
        ("Key detail", "AC-CPC: InfoNCE prediction of latent features K = 10 steps (~0.67 s) ahead, conditioned on future actions; without the action conditioning HNS drops from 162/77 to 111/42"),
    ],
    "evidence": "verified",
    "sources": ["verified_findings Finding 5 (arXiv 2503.04416 Tables 4, 6, 7, 9; github.com/burchim/TWISTER att_context_left = 8)",
                "arXiv 2503.04416 Sec. 3.1-3.2, App. A.3 Table 9"],
    "diagram": {
        "encoder": {"text": "Frame 64x64 → CNN categorical VAE", "sub": "32 categoricals × 32 classes per frame",
                    "tag": "trained jointly", "short": "CNN VAE, 32×32 categoricals"},
        "tokens": {"groups": [("latent", 1, "1 fused token: z_t + a_t")],
                   "note": "per step; attention context 8 steps"},
        "core": {"title": "TSSM ×4 · d 512 · 8 heads",
                 "rows": [("action", "Action mixer: z_t and a_t → one token"),
                          ("attn", "Causal self-attention, relative positions"),
                          ("mlp", "MLP (FFN 1024)")],
                 "notes": ["Transformer-XL style: previous segment cached, capped at 8 steps"]},
        "sampling": {"kind": "ar", "text": "Next state: categorical sample, 32×32",
                     "sub": "1 pass per imagined step; AC-CPC head trains 10 steps ahead", "short": "Next state, 1 pass per step"},
        "heads": ["reward", "continue"],
        "decoder": {"none": "actor-critic uses {h_t, z_t}; the CNN decoder only trains the VAE"},
        "loop": "AR rollout",
    },
}
