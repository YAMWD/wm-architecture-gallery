MODEL = {
    "slug": "jowa",
    "name": "JOWA",
    "year": 2024, "month": 10,
    "org": "CASIA / Alibaba",
    "family": "rl",
    "role": "Discrete-token model",
    "status": "ICLR 2025",
    "params": "150M (also 70M, 40M)",
    "params_num": 150e6,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2410.00564", "code": "https://github.com/CJReinforce/JOWA"},
    "summary": "An offline, multi-game world-action model: one GPT-2-style transformer over IRIS-like token sequences learns "
               "the world model (next observation tokens, reward, termination) and the Q-function at the same time, "
               "pretrained on 15 Atari games with 10M transitions each. At decision time a short beam search (horizon 2) "
               "over the model's own imagined futures corrects the Q-estimates. Beams are batched, but every imagined "
               "frame still costs 36 sequential token decodes, and planning drops throughput from 10.8 to 1.26 FPS.",
    "facts": [
        ("Representation", "VQ-VAE on 84×84 grayscale frames: 36 tokens per frame (6×6 [D]), vocabulary 2048; "
                           "3-layer CNN with self-attention at resolutions 6 and 12 (IRIS code base), frozen after stage 1"),
        ("Core", "GPT-2 (minGPT): JOWA-150M 12 layers, hidden 768, 12 heads; JOWA-70M 6 × 768 × 12; JOWA-40M 4 × 512 × 8; "
                 "dropout 0.1; input = vocabulary + position + learnable task embedding"),
        ("Attention", "Causal over interleaved (z_t^1..z_t^36, a_t) tokens; L = 8 steps, max 296 tokens (8 × 37 [D])"),
        ("Actions", "One action token per step (18-action Atari space) plus a task embedding; the Q-head reads the "
                    "transformer output at the observation tokens"),
        ("Prediction", "Next observation token autoregressive within a frame, z_t^k | z_≤t-1, z_t^<k, a_≤t-1, so 36 serial "
                       "decodes per imagined frame [D]; reward sign {-1, 0, 1} and termination as classification; "
                       "distributional Q-head (3-layer MLP, hidden 1792, 3 heads for 150M) trained by TD learning"),
        ("Decoder", "VQ-VAE CNN decoder for reconstruction only; planning and Q-values stay in token space"),
        ("Memory", "Context of 8 steps = 296 tokens; no KV-cache details given"),
        ("Speed", "JOWA-150M on 7 games: 10.8 FPS without planning, 1.26 FPS with beam search (H = 2, K = 2-4), 0.12 FPS with "
                  "MCTS; hardware not stated (authors, Table 5). Pretraining 1.75M steps, 'around 12 days on A100 GPUs', GPU "
                  "count not given"),
        ("Key detail", "Beam search calls the world model K²(H−1)+K times but takes only H forward latencies because beams are "
                       "batched; at H = 2 that is still ~72 serial token decodes per action [D], ~0.8 s at 1.26 FPS [D]"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2410.00564 Sec. 3 (84×84, 18 actions), Sec. 4.1-4.2 (architecture, Eq. 4-6, beam search cost), Sec. 5 (K = 36, L = 8, H = 2)",
                "arXiv 2410.00564 Table 5 (FPS), Tables 9-12 (VQ-VAE, transformer, Q-head configs), Table 17 (beam widths), Sec. 3 (12 A100-days)"],
    "diagram": {
        "encoder": {"text": "Frame 84×84 → VQ-VAE (CNN)", "sub": "36 codes per frame, vocab 2048", "tag": "frozen",
                    "short": "VQ-VAE, 36 codes per frame"},
        "tokens": {"groups": [("frame", 36, "36 frame codes"), ("action", 1, "action")],
                   "note": "per step; context 8 steps = 296 tokens"},
        "core": {"title": "GPT-2 ×12 · d 768 · 12 heads (150M)",
                 "rows": [("attn", "Causal self-attention over tokens"),
                          ("mlp", "MLP")],
                 "notes": ["learnable task embedding on observation and action tokens", "variants: 6 × 768 (70M), 4 × 512 (40M)"]},
        "sampling": {"kind": "search", "text": "Beam search on Q + reward, horizon 2",
                     "sub": "36 serial token decodes per imagined frame; beams batched",
                     "short": "Beam search, horizon 2, width 2–4"},
        "heads": ["reward", "termination", "Q-values"],
        "decoder": {"text": "VQ decoder (CNN) → 84×84 frame", "sub": "reconstruction only; planning stays in token space", "tag": "frozen",
                    "short": "VQ decoder (not used in planning)"},
        "loop": "beam search",
    },
    "flow": {
        "below": [{"text": "Atari frame 84×84 + action + task ID"}],
        "stack": [
            {"box": "VQ-VAE encoder (CNN)", "id": "enc", "style": "teal"},
            {"box": "Nearest codebook entry", "id": "vq"},
            {"box": "Token embedding", "id": "emb", "minor": True},
            {"group": [
                {"residual": [{"box": "LayerNorm", "minor": True},
                              {"box": "Masked self-attention", "id": "attn", "style": "dark", "side": "Position + task emb."}]},
                {"residual": [{"box": "LayerNorm", "minor": True}, {"box": "Feed forward", "id": "ffn"}]},
            ], "repeat": "12 ×", "id": "block"},
            {"fanout": [[{"box": "Next-code head", "id": "out", "minor": True}, {"box": "Sample next code", "id": "sample"}],
                        [{"box": "Reward head", "id": "rew", "terminal": True, "minor": True}],
                        [{"box": "Done head", "terminal": True, "minor": True}],
                        [{"box": "Q-value head", "id": "q", "terminal": True}]]},
        ],
        "above": [{"box": "VQ-VAE decoder (CNN)", "id": "dec", "style": "teal"}, {"text": "Next frame 84×84 (reconstruction only)"}],
        "insets": [
            {"for": "ffn", "stack": [{"box": "Linear"}, {"box": "GELU"}, {"box": "Linear"}]},
            {"for": "q", "label": "Q-value head", "stack": [{"box": "Linear, LayerNorm, Mish"}, {"box": "Linear, LayerNorm, Mish"}, {"box": "Linear → return bins"}]},
        ],
        "annotations": [
            {"at": "vq", "text": "*36* codes per frame (*6×6* [D]), vocabulary *2,048*", "side": "left", "key": True},
            {"at": "emb", "text": "width *768*; learnable task embedding added to observation and action tokens; VQ-VAE frozen after stage 1", "side": "left"},
            {"at": "attn", "text": "*12* heads; causal over (*36* codes + action) per step; context *8* steps = *296* tokens", "side": "left", "key": True},
            {"at": "block", "text": "*12* layers, *150M* parameters (also 70M and 40M variants); dropout *0.1*", "side": "right", "key": True},
            {"at": "sample", "text": "beam search, H *2*, K *2–4*: expand the top-K actions by Q, imagine the next frame (*36* serial decodes [D]), score reward + Q, keep the best beams", "side": "left"},
            {"at": "out", "text": "next-code, reward and done heads are *2*-layer MLPs; the Q-head a *3*-layer MLP (hidden *1,792*, *3* distributional heads) trained by TD with CQL", "side": "right"},
            {"at": "q", "text": "*10.8* FPS without planning, *1.26* FPS with beam search H *2* (authors; hardware not stated)", "side": "right", "key": True},
            {"at": "dec", "text": "reconstruction only; planning and Q-values stay in token space", "side": "right"},
        ],
        "feedback": "next step",
    },
}
