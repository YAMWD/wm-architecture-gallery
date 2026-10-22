MODEL = {
    "slug": "rem",
    "name": "REM",
    "year": 2024, "month": 2,
    "org": "Technion",
    "family": "rl",
    "role": "Discrete-token model",
    "status": "ICML 2024",
    "params": "size not disclosed (~4M [D])",
    "params_num": None,
    "open": "code",
    "links": {"arXiv": "https://arxiv.org/abs/2402.05643", "code": "https://github.com/leor-c/REM"},
    "summary": "An IRIS-style token world model whose transformer is replaced by a Retentive Network and whose per-token "
               "decode loop is removed. Retention keeps a fixed-size recurrent state instead of a KV cache, and Parallel "
               "Observation Prediction (POP) feeds 64 learned prediction tokens from that state to sample all 64 next-frame "
               "codes in one call. Imagination becomes 2 calls per frame instead of 64, which the authors measure as 15.4× "
               "faster than prior token-based world models.",
    "tagline": "RetNet over VQ codes, a whole frame at a time",
    "facts": [
        ("Representation", "64 VQ codes per 64×64 frame (8×8 grid), vocabulary 512; VQ-GAN-style CNN tokenizer without the "
                           "discriminator (IRIS uses 16 codes)"),
        ("Core", "RetNet (retention, not softmax attention): 5 layers, 4 retention heads, d 256, FFN 1024, dropout 0.1; "
                 "parameter count not disclosed (~3.9M block weights [D]); FFN activation not disclosed"),
        ("Attention", "Multi-scale retention with a per-head exponential decay and relative position; chunkwise mode is parallel "
                      "inside a chunk of c = 3 observation-action blocks (195 tokens [D]) and recurrent between chunks through a "
                      "d×d state per head; world-model context 2 frames"),
        ("Actions", "One action token per step (learned embedding) after the 64 observation tokens; reward and "
                    "termination are read from the action token; the world model reuses the tokenizer's embedding table"),
        ("Prediction", "POP: K = 64 learned prediction tokens u are run from the recurrent state S_t and all next-frame tokens are "
                       "sampled in one pass; default mode = 2 sequential calls per imagined frame (state update with z_t, a_t, "
                       "then prediction with u), so 2H calls over the horizon H = 10 instead of KH = 640 (Table 6)"),
        ("Decoder", "VQ-VAE CNN decoder for the reconstruction loss only; the actor-critic reads the token code vectors through "
                    "a small CNN + LSTM, so imagination decodes no pixels"),
        ("Memory", "Fixed-size retention state per layer and head replaces a growing KV cache; u tokens never enter the state update"),
        ("Speed", "15.4× faster imagination than prior token-based world models and under 12 h of training per game (authors); "
                  "run times measured on an RTX 4090 workstation, other experiments on V100s"),
        ("Key detail", "POP doubles the tokens per observation prediction (2K vs K, Table 6) but turns KH sequential calls into 2H; "
                       "superhuman on 12 of 26 Atari 100k games (authors)"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2402.05643 Sec. 2.2-2.4 (retention, POP, training), Fig. 4, Sec. 4 (K = 64, RTX 4090 / V100), abstract (15.4×, < 12 h)",
                "arXiv 2402.05643 Table 2 (H 10, N 512, 64×64), Table 5 (world-model config), Table 6 (call counts), Table 8 and A.1.3 (actor-critic input)"],
    "diagram": {
        "encoder": {"text": "Frame 64×64 → VQ-VAE (CNN)", "sub": "64 codes per frame (8×8), vocab 512", "tag": "trained jointly",
                    "short": "VQ-VAE, 64 codes per frame"},
        "tokens": {"groups": [("frame", 64, "64 frame codes"), ("action", 1, "action"), ("register", 4, "64 prior tokens u")],
                   "note": "per step; chunk c = 3 blocks; context 2 frames"},
        "core": {"title": "RetNet ×5 · d 256 · 4 heads",
                 "rows": [("ssm", "Retention (recurrent across chunks)"),
                          ("mlp", "FFN 1024")],
                 "notes": ["d×d recurrent state per head replaces the KV cache", "POP: u tokens read S_t, never update it"]},
        "sampling": {"kind": "parallel", "text": "POP: all 64 next-frame tokens in one call", "sub": "2 sequential calls per imagined frame; horizon 10",
                     "short": "POP: 64 tokens per call"},
        "heads": ["reward", "termination"],
        "decoder": {"text": "VQ decoder (CNN) → 64×64 frame", "sub": "reconstruction loss only; actor-critic reads token codes", "tag": "trained jointly",
                    "short": "VQ decoder (loss only)"},
        "loop": "AR rollout",
    },
    "flow": {
        "below": [{"text": "Atari frame 64×64 + action"}],
        "stack": [
            {"box": "VQ-VAE encoder (CNN)", "id": "enc", "style": "teal"},
            {"box": "Nearest codebook entry", "id": "vq", "minor": True},
            {"box": "Embed codes + u tokens", "short": "Embed + u tokens", "id": "emb", "side": "Action emb."},
            {"group": [
                {"residual": [{"box": "LayerNorm", "minor": True},
                              {"box": "Multi-scale retention", "id": "ret", "style": "dark", "side": "Relative positions"}]},
                {"residual": [{"box": "LayerNorm", "minor": True}, {"box": "Feed forward", "id": "ffn"}]},
            ], "repeat": "5 ×", "id": "block"},
            {"fanout": [[{"box": "POP: all codes at once", "id": "sample"}],
                        [{"box": "Reward head", "id": "rew", "terminal": True, "minor": True}],
                        [{"box": "Done head", "terminal": True, "minor": True}]]},
        ],
        "above": [{"box": "VQ-VAE decoder (CNN)", "id": "dec", "style": "teal"}, {"text": "Next frame 64×64 (loss only)"}],
        "insets": [
            {"for": "sample", "stack": [{"box": "Update S_t with z_t, a_t"}, {"box": "Run u from S_t"}, {"box": "All codes in parallel"}]},
        ],
        "annotations": [
            {"at": "enc", "text": "*64* codes per frame · vocabulary of *512*", "side": "left", "key": True},
            {"at": "emb", "text": "*64* prediction tokens u", "side": "right", "key": True},
            {"at": "ret", "text": "*4* heads · width *256*", "side": "left"},
            {"at": "block", "text": "*5* layers · ~*3.9M* block weights", "side": "right", "key": True},
            {"at": "sample", "text": "*2* calls per frame · imagination *15.4×* faster", "side": "left", "key": True},
        ],
        "feedback": "next step",
    },
}
