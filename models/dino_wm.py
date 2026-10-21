MODEL = {
    "slug": "dino_wm",
    "name": "DINO-WM",
    "year": 2024, "month": 11,
    "org": "NYU",
    "family": "jepa",
    "role": "Embedding predictor",
    "status": "ICML 2025",
    "params": "~19M predictor + frozen DINOv2",
    "params_num": 19e6,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2411.04983", "code": "https://github.com/gaoyuezhou/dino_wm",
              "page": "https://dino-wm.github.io"},
    "summary": "A task-agnostic latent world model that predicts future DINOv2 patch features instead of pixels. A frozen "
               "DINOv2 turns each 196x196 frame into 196 patch features of width 384, and a small ViT predictor "
               "(6 layers, ~19M parameters) regresses the next frame's features from a history of 3 frames, with the "
               "action and proprioception embeddings concatenated onto every patch vector rather than added as tokens. "
               "Goals are images; planning is cross-entropy-method search in feature space, and the pixel decoder "
               "exists only for visualization.",
    "facts": [
        ("Representation", "196 patch features (14x14 x 384) per frame resized to 196x196, from a frozen DINOv2 encoder "
                           "(variant not named in the paper; 384-d is the ViT-S/14 size [D])"),
        ("Core", "ViT with the patch-embedding layer removed, used as a decoder-only predictor: depth 6, 16 heads, MLP 2048, "
                 "~19M parameters; token width = 384 features + 10-d action embedding (+ 10-d proprio) [D]"),
        ("Attention", "Frame-level causal mask: every patch of frame t attends to all patches of frames t-H..t-1 (no "
                      "token-level autoregression); H = 3 (PointMaze, Reacher, Push-T, PushObj) or 1 (Wall, Rope, Granular); "
                      "at most 3 x 196 = 588 tokens [D]"),
        ("Actions", "An MLP maps the action to a 10-d embedding that is concatenated to every patch vector (channels, not "
                    "tokens); proprioception enters the same way; frameskip 5 (1 for Rope and Granular)"),
        ("Prediction", "One pass regresses the next frame's 196 features (MSE in latent space); no sampling, no pixels"),
        ("Decoder", "Optional transposed-convolution decoder trained separately, for visualization only; training the "
                    "predictor through its loss lowers Push-T success (0.92 → 0.80)"),
        ("Memory", "Fixed window of H frames; no KV cache or long-term memory"),
        ("Speed", "One predictor step at batch 32: 0.014 s; a full CEM plan (100 samples x 10 iterations): 53.0 s, both on "
                  "one A6000 (authors); LeWM later measured 47 s per DINO-WM plan (hardware not stated)"),
        ("Key detail", "196 tokens per frame make every CEM sample a 588-token ViT pass; LeWM's one-token-per-frame design "
                       "runs the same kind of plan in ~1 s"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2411.04983 Sec. 3.1 (encoder, predictor, decoder, planning), App. A.4.2-A.4.3, A.5.1, Table 10 (timing), "
                "A.9 and Tables 11-12 (hyperparameters)",
                "GitHub gaoyuezhou/dino_wm conf/predictor/vit.yaml (depth 6, heads 16, mlp_dim 2048) and conf/train.yaml "
                "(action and proprio emb dim 10, num_hist 3, frameskip 5); fetched, no explicit width",
                "LeWM arXiv 2603.19312 Fig. 3 (47 s DINO-WM plan)"],
    "diagram": {
        "encoder": {"text": "Frame 196x196 → DINOv2 encoder", "sub": "196 patch features × 384 per frame", "tag": "frozen",
                    "short": "DINOv2, 196 patch features"},
        "tokens": {"groups": [("latent", 14, "196 patch features")],
                   "note": "per frame; history H = 3 frames = 588 tokens"},
        "core": {"title": "ViT predictor ×6 · 16 heads · MLP 2048",
                 "rows": [("attn", "Frame-level causal self-attention"),
                          ("action", "Action + proprio embeddings (10-d) concatenated to every patch"),
                          ("mlp", "MLP (2048)")],
                 "notes": ["window H = 3 frames; no KV cache"]},
        "sampling": {"kind": "regress", "text": "Next-frame features, MSE regression", "sub": "1 pass per step; no sampling"},
        "decoder": {"none": "planning by CEM in feature space: 100 samples × 10 iterations; decoder only for visualization"},
        "loop": "CEM rollout",
    },
}
