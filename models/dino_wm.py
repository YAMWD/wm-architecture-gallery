MODEL = {
    "slug": "dino_wm",
    "name": "DINO-WM",
    "year": 2024, "month": 11,
    "org": "NYU",
    "family": "jepa",
    "role": "Embedding predictor",
    "status": "ICML 2025",
    "params": "~19M + frozen DINOv2",
    "params_num": 19e6,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2411.04983", "code": "https://github.com/gaoyuezhou/dino_wm",
              "page": "https://dino-wm.github.io"},
    "tagline": "Predicts DINOv2 patch features, plans by CEM",
    "summary": "A task-agnostic latent world model that predicts future DINOv2 patch features instead of pixels. A frozen "
               "DINOv2 turns each 196x196 frame into 196 patch features of width 384, and a small ViT predictor "
               "(6 layers, ~19M parameters) regresses the next frame's features from a history of up to 3 frames, with the "
               "action and proprioception embeddings concatenated onto every patch vector rather than added as tokens. "
               "Goals are images; planning is cross-entropy-method search in feature space, and the pixel decoder "
               "exists only for visualization.",
    "facts": [
        ("Representation", "196 patch features (14x14 x 384) per frame resized to 196x196, from a frozen DINOv2 ViT-S/14 "
                           "(dinov2_vits14 in the official config; the paper does not name the variant)"),
        ("Core", "ViT with the patch-embedding layer removed, used as a decoder-only predictor: depth 6, 16 heads, MLP 2048, "
                 "~19M parameters (paper; the predictors in the released checkpoints have 20.1M at H = 3 and 19.96M at "
                 "H = 1 [D]); token width 404 = 384 features + 10-d action + 10-d proprio (official code); the code also "
                 "uses pre-LayerNorm blocks, GELU in the MLP, a learned absolute position embedding per (frame, patch) "
                 "slot added once at the input, and a final LayerNorm, none of which the paper describes"),
        ("Attention", "Frame-level causal mask: every patch of frame t attends to all patches of frames t-H..t-1 (no "
                      "token-level autoregression); H = 3 (PointMaze, Reacher, Push-T, PushObj) or 1 (Wall, Rope, Granular); "
                      "at most 3 x 196 = 588 tokens [D]"),
        ("Actions", "A linear layer (a 1x1 Conv1d in the official code and weights; the paper calls it an MLP) maps the "
                    "frameskip-stacked action to a 10-d embedding that is concatenated to every patch vector (channels, "
                    "not tokens); proprioception enters the same way through its own 10-d linear layer; frameskip 5 "
                    "(1 for Rope and Granular)"),
        ("Prediction", "One pass regresses the next frame's 196 features (MSE in latent space); no sampling, no pixels"),
        ("Decoder", "Optional transposed-convolution decoder trained separately, for visualization only; training the "
                    "predictor through its loss lowers Push-T success (0.92 → 0.80)"),
        ("Memory", "Fixed window of H frames; no KV cache or long-term memory"),
        ("Speed", "One world-model forward step at batch 32: 0.014 s; a full CEM plan (100 samples x 10 iterations): "
                  "15.89 s in the ICML 2025 camera-ready (App. A.6, Table 11; arXiv v2 Table 10 gave 53.0 s), both on "
                  "one A6000 (authors); LeWM later measured 47 s per DINO-WM plan in its own CEM setup (hardware not "
                  "stated)"),
        ("Key detail", "196 tokens per frame make each CEM sample a 5-step predictor rollout (released horizon 5) whose "
                       "window grows from 196 to 588 tokens at H = 3, with all samples of an iteration run as one batch "
                       "[D]; LeWM's one-token-per-frame design runs the same kind of plan in ~1 s (0.98 s vs 47 s in "
                       "LeWM's measurement)"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2411.04983v2 Sec. 3.1-3.2, App. A.4.2-A.4.3, A.5.1, A.8 Table 10, A.9 Tables 11-12",
                "ICML 2025 camera-ready, PMLR 267:79115-79135, App. A.6 Table 11 (inference and planning time)",
                "GitHub gaoyuezhou/dino_wm: models/vit.py, models/proprio.py, models/visual_world_model.py, train.py, "
                "planning/cem.py, conf/encoder/dino.yaml, conf/predictor/vit.yaml, conf/train.yaml, conf/plan_pusht.yaml",
                "Released checkpoints (OSF bmw48 checkpoints/outputs.zip: hydra.yaml configs, tensor shapes)",
                "LeWM arXiv 2603.19312 Sec. 3.1, Fig. 3 (47 s vs 0.98 s per plan)"],
    "audit": {"date": "2026-10-22", "checked": 45, "stated": 27, "code": 16, "derived": 2, "assumed": 0, "fixed": 10},
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
    "flow": {
        "below": [{"text": "Frame 196×196 + action + proprio"}],
        "stack": [
            {"box": "Frozen DINOv2 encoder", "id": "enc", "style": "teal", "basis": "stated"},
            {"box": "Patch features", "id": "feat", "minor": True, "basis": "stated"},
            {"box": "Concat action + proprio", "id": "cat", "style": "orange", "side": "Linear embeddings",
             "basis": "stated", "side_basis": "code"},
            {"group": [
                {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"},
                              {"box": "Frame-causal attention", "id": "attn", "style": "dark", "basis": "stated"}]},
                {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"}, {"box": "MLP", "id": "mlp", "basis": "stated"}]},
            ], "repeat": "6 ×", "id": "block", "basis": "code"},
            {"box": "Next-frame features", "id": "pred", "basis": "stated"},
        ],
        "above": [{"text": "MSE distance to the goal features"}],
        "insets": [{"for": "mlp", "stack": [{"box": "Linear", "basis": "code"}, {"box": "GELU", "basis": "code"},
                                            {"box": "Linear", "basis": "code"}]},
                   {"for": "pred", "label": "planning loop", "stack": [{"box": "Sample action sequences", "basis": "stated"},
                                                                       {"box": "Roll the predictor out", "basis": "stated"},
                                                                       {"box": "MSE to the goal features", "basis": "stated"},
                                                                       {"box": "Refit Gaussian to top K", "basis": "stated"}]}],
        "annotations": [
            {"at": "enc", "text": "*196* tokens per frame · width *384*", "side": "left", "key": True},
            {"at": "cat", "text": "*10*-d action + proprio on each patch", "side": "left"},
            {"at": "attn", "text": "*16* heads · up to *588* tokens (*3* frames)", "side": "left", "key": True},
            {"at": "mlp", "text": "MLP hidden size *2,048*", "side": "left"},
            {"at": "block", "text": "*6* layers · ~*19M* parameters", "side": "right", "key": True},
            {"at": "pred", "text": "*15.89* s per plan: *100* samples × *10* steps", "side": "left", "key": True},
        ],
        "feedback": "CEM rollout",
    },
}
