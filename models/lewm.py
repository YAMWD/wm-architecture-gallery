MODEL = {
    "slug": "lewm",
    "name": "LeWorldModel (LeWM)",
    "year": 2026, "month": 3,
    "org": "Mila, NYU",
    "family": "jepa",
    "role": "Embedding predictor",
    "status": "arXiv preprint (v3 Jun 2026)",
    "params": "~18M total (paper: 15M); predictor ~10.8M",
    "params_num": 18e6,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2603.19312", "code": "https://github.com/lucas-maes/le-wm",
              "page": "https://le-wm.github.io", "weights": "https://huggingface.co/collections/quentinll/lewm"},
    "tagline": "One token per frame, CEM plans in under a second",
    "summary": "The smallest JEPA world model in the gallery: a ViT-Tiny encoder and a 6-layer predictor trained end to "
               "end from pixels with two losses only (next-embedding MSE plus the SIGReg Gaussian regularizer), with no "
               "EMA, stop-gradient or frozen foundation encoder. Each frame is squeezed into a single 192-d [CLS] "
               "embedding, so the predictor sees at most 3 tokens, and a CEM plan of 300 samples x up to 30 iterations "
               "x horizon 5 finishes in 0.98 s against 47 s for DINO-WM.",
    "facts": [
        ("Representation", "One 192-d token per 224x224 frame: the last-layer [CLS] embedding of a ViT-Tiny (patch 14, "
                           "12 layers, 3 heads, width 192, ~5M) followed by a 1-layer MLP projector with BatchNorm"),
        ("Core", "Predictor: 6 layers, d 192, 16 heads of 64, MLP 2048, dropout 0.1, learned positional embeddings; ~10M; "
                 "followed by a projector of the same design as the encoder's"),
        ("Attention", "Temporal causal mask over the history of frame embeddings; N = 3 frames (paper: 1 for TwoRoom; the "
                      "released TwoRoom checkpoint and code use 3), i.e. at most 3 tokens per predictor call [D]"),
        ("Actions", "Zero-initialised AdaLN at every predictor layer; with frameskip 5 the 5 actions between frames form "
                    "one 10-d action block, embedded to width 192"),
        ("Prediction", "One pass regresses the next frame embedding (MSE); encoder and predictor trained jointly, SIGReg "
                       "keeps the embeddings Gaussian to prevent collapse"),
        ("Decoder", "None in training or planning; a diagnostic cross-attention decoder (196 queries → 224x224) only "
                    "visualizes what the latent retains"),
        ("Memory", "Window of N = 3 frame embeddings; no KV cache"),
        ("Speed", "Full plan 0.98 s vs 47 s for DINO-WM, averaged over 50 runs (authors; GPU not stated); CEM with 300 "
                  "samples, top 30, up to 30 iterations (PushT) or 10, horizon 5 latent steps = 25 environment steps, "
                  "whole plan executed before replanning"),
        ("Key detail", "196x fewer tokens per frame than DINO-WM [D]; a PushT plan is 150 sequential batched calls "
                       "(30 iterations x 5 predictor steps), each over 300 candidates with windows of 1, 2, 3, 3, 3 tokens: "
                       "~7-21 GFLOP per call, ~2.5 TFLOP per plan [D], a latency-bound chain rather than a throughput job"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2603.19312 Sec. 3 (architecture, planning), Sec. 4.2 and Fig. 3 (timing), App. D (encoder, "
                "predictor, decoder, planning solver)",
                "Hugging Face quentinll/lewm-pusht config.json (predictor d 192, head dim 64, MLP 2048, history 3)",
                "GitHub lucas-maes/le-wm README, module.py, jepa.py, config/eval/solver/cem.yaml",
                "Hugging Face quentinll/lewm-pusht and lewm-tworooms weights.pt (parameter count)"],
    "figure_variant": "Released LeWM: ViT-Tiny encoder + 6-layer predictor",
    "flow": {
        "below": [{"text": "Frame 224×224 + action block"}],
        "stack": [
            {"box": "ViT-Tiny encoder", "id": "enc", "style": "teal", "basis": "stated"},
            {"box": "[CLS] token + projector", "short": "[CLS] + projector", "id": "cls", "basis": "stated"},
            {"box": "History of frame tokens", "id": "hist", "minor": True, "basis": "stated", "side": "Learned positions", "side_basis": "code"},
            {"group": [
                {"residual": [{"box": "AdaLN, zero-initialised", "short": "AdaLN (actions)", "id": "ada", "style": "orange", "side": "Action emb.", "basis": "stated", "side_basis": "code"},
                              {"box": "LayerNorm", "minor": True, "basis": "code"},
                              {"box": "Causal self-attention", "id": "attn", "style": "dark", "basis": "stated"},
                              {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                {"residual": [{"box": "AdaLN", "minor": True, "basis": "code"},
                              {"box": "LayerNorm", "minor": True, "basis": "code"},
                              {"box": "MLP", "id": "mlp", "basis": "code"},
                              {"box": "Scale by gate", "minor": True, "basis": "code"}]},
            ], "repeat": "6 ×", "id": "block"},
            {"box": "Final LayerNorm", "minor": True, "basis": "code"},
            {"box": "Projector", "id": "proj", "minor": True, "basis": "stated"},
            {"box": "Next-frame embedding", "id": "pred", "basis": "stated"},
        ],
        "above": [{"text": "Squared L2 to the goal embedding"}],
        "insets": [{"for": "mlp", "stack": [{"box": "Linear", "basis": "code"}, {"box": "GELU", "basis": "code"}, {"box": "Linear", "basis": "code"}]},
                   {"for": "pred", "label": "planning loop", "stack": [{"box": "Sample 300 sequences", "basis": "stated"}, {"box": "Roll out 5 latent steps", "basis": "stated"},
                                                                       {"box": "Squared L2 to goal", "basis": "stated"}, {"box": "Refit the Gaussian, ≤30×", "basis": "stated"}]}],
        "annotations": [
            {"at": "enc", "text": "*12* layers · *3* heads · ~*5M*", "side": "left"},
            {"at": "cls", "text": "*1* token per frame · embedding *192*", "side": "left", "key": True},
            {"at": "ada", "text": "*10*-d block of *5* actions", "side": "left"},
            {"at": "attn", "text": "*16* heads over *3* tokens", "side": "left", "key": True},
            {"at": "block", "text": "*6* layers · ~*10M* parameters", "side": "right", "key": True},
            {"at": "pred", "text": "*0.98* s per CEM plan · DINO-WM *47* s", "side": "left", "key": True},
        ],
        "feedback": "predicted embedding",
        "feedback_from": "pred",
        "feedback_to": "hist",
    },
}
