MODEL = {
    "slug": "lewm",
    "name": "LeWorldModel (LeWM)",
    "year": 2026, "month": 3,
    "org": "Mila, NYU",
    "family": "jepa",
    "role": "Embedding predictor",
    "status": "arXiv preprint (v3 Jun 2026)",
    "params": "~15M total (10M predictor)",
    "params_num": 15e6,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2603.19312", "code": "https://github.com/lucas-maes/le-wm",
              "page": "https://le-wm.github.io", "weights": "https://huggingface.co/collections/quentinll/lewm"},
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
        ("Attention", "Temporal causal mask over the history of frame embeddings; N = 3 frames (PushT, OGBench-Cube) or 1 "
                      "(TwoRoom), i.e. at most 3 tokens per predictor call [D]"),
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
                       "(30 iterations x horizon 5) of ~18 GFLOP each [D], a latency-bound chain rather than a "
                       "throughput job"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2603.19312 Sec. 3 (architecture, planning), Sec. 4.2 and Fig. 3 (timing), App. D (encoder, "
                "predictor, decoder, planning solver)",
                "Hugging Face quentinll/lewm-pusht config.json (predictor d 192, head dim 64, MLP 2048, history 3; "
                "fetched)",
                "GitHub lucas-maes/le-wm README (checkpoints, code base)"],
    "diagram": {
        "encoder": {"text": "Frame 224x224 → ViT-Tiny (5M) + projector", "sub": "one 192-d [CLS] embedding per frame",
                    "tag": "trained jointly", "short": "ViT-Tiny, 1 token per frame"},
        "tokens": {"groups": [("latent", 1, "1 frame embedding (192-d)")],
                   "note": "per frame; history N = 3 frames = 3 tokens"},
        "core": {"title": "Predictor ×6 · d 192 · 16 heads",
                 "rows": [("attn", "Temporal causal self-attention over 3 frame embeddings"),
                          ("action", "Action block via zero-initialised AdaLN at every layer"),
                          ("mlp", "MLP (2048)")],
                 "notes": ["learned positional embeddings; no KV cache"]},
        "sampling": {"kind": "regress", "text": "Next-frame embedding, MSE regression + SIGReg",
                     "sub": "1 pass per step; no sampling", "short": "Next embedding, 1 pass per step"},
        "decoder": {"none": "planning by CEM in latent space: 300 samples × ≤30 iterations × horizon 5"},
        "loop": "CEM rollout",
    },
    "flow": {
        "below": [{"text": "Frame 224×224 + action block"}],
        "stack": [
            {"box": "ViT-Tiny encoder", "id": "enc", "style": "teal"},
            {"box": "[CLS] embedding + projector", "short": "[CLS] + projector", "id": "cls"},
            {"box": "History of frame tokens", "id": "hist", "minor": True},
            {"group": [
                {"residual": [{"box": "AdaLN, zero-initialised", "short": "AdaLN (actions)", "id": "ada", "style": "orange", "side": "Action emb."},
                              {"box": "Temporal causal self-attention", "short": "Causal self-attention", "id": "attn", "style": "dark",
                               "side": "Learned positions"}]},
                {"residual": [{"box": "AdaLN", "minor": True}, {"box": "MLP", "id": "mlp"}]},
            ], "repeat": "6 ×", "id": "block"},
            {"box": "Projector", "id": "proj", "minor": True},
            {"box": "Predicted next-frame embedding", "short": "Next-frame embedding", "id": "pred"},
        ],
        "above": [{"text": "MSE distance to the goal embedding"}],
        "insets": [{"for": "mlp", "stack": [{"box": "Linear"}, {"box": "GELU"}, {"box": "Linear"}]},
                   {"for": "pred", "label": "planning loop", "stack": [{"box": "Sample 300 action sequences"}, {"box": "Roll out 5 latent steps"},
                                                                       {"box": "MSE to the goal embedding"}, {"box": "Refit the Gaussian, ≤30×"}]}],
        "annotations": [
            {"at": "enc", "text": "ViT-Tiny, ~*5M*, trained end to end with the predictor (MSE + SIGReg, no decoder): patch *14*, *12* layers, *3* heads, width *192*", "side": "left"},
            {"at": "cls", "text": "*1* token of width *192* per frame: the [CLS] embedding through a 1-layer MLP projector with BatchNorm; *196×* fewer tokens than DINO-WM [D]",
             "short": "*1* token of width *192* per frame ([CLS] + projector)", "side": "left", "key": True},
            {"at": "ada", "text": "zero-initialised AdaLN at every layer; the *5* actions between frames form one *10*-d action block embedded to width *192*", "side": "left"},
            {"at": "attn", "text": "*16* heads of *64*; causal over N = *3* frame embeddings = *3* tokens", "side": "left", "key": True},
            {"at": "block", "text": "*6* layers, MLP *2,048*, dropout *0.1*, ~*10M* parameters", "side": "right", "key": True},
            {"at": "pred", "text": "one CEM plan (*300* samples × ≤*30* iterations × horizon *5*) takes *0.98* s vs *47* s for DINO-WM (authors; GPU not stated)",
             "short": "CEM plan: *0.98* s vs *47* s for DINO-WM", "side": "left", "key": True},
        ],
        "feedback": "CEM rollout",
    },
}
