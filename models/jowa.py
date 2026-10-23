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
    "tagline": "One GPT for Atari dynamics and Q-values",
    "facts": [
        ("Representation", "VQ-VAE on 84×84 grayscale frames: 36 tokens per frame (6×6 [D]), vocabulary 2048; "
                           "3-layer CNN with self-attention at resolutions 6 and 12 (IRIS code base), frozen after stage 1"),
        ("Core", "GPT-2 (minGPT): JOWA-150M 12 layers, hidden 768, 12 heads; JOWA-70M 6 × 768 × 12; JOWA-40M 4 × 512 × 8; "
                 "dropout 0.1; input = vocabulary + position + learnable task embedding"),
        ("Attention", "Causal over interleaved (z_t^1..z_t^36, a_t) tokens; L = 8 steps, max 296 tokens (8 × 37 [D])"),
        ("Actions", "One action token per step (18-action Atari space) plus a task embedding; the Q-head reads the "
                    "output at the last observation token z_t^36 of each step, the reward and done heads the action token; "
                    "next-code, reward and done heads are 2-layer MLPs; the JOWA-150M Q-head is a 3-layer MLP (hidden 1,792, "
                    "3 distributional heads; 40M and 70M: 1 head, hidden 768 and 1,024) trained by TD with CQL"),
        ("Prediction", "Next observation token autoregressive within a frame, z_t^k | z_≤t-1, z_t^<k, a_≤t-1, so 36 serial "
                       "decodes per imagined frame [D]; reward sign {-1, 0, 1} and termination as classification; "
                       "distributional Q-head (3-layer MLP, hidden 1792, 3 heads for 150M) trained by TD learning"),
        ("Decoder", "VQ-VAE CNN decoder; decisions use only token-space heads, but the released code decodes every "
                    "imagined frame during beam search (K + K² frames per action, output discarded) and turns decoded "
                    "imagined frames into synthetic fine-tuning data"),
        ("Memory", "Context up to 8 steps = 296 tokens; with planning at most 8 − H = 6 real steps plus 2 imagined. The paper "
                   "gives no cache details; the released code keeps a per-layer KV cache (prefill once, then single-token "
                   "cached passes; per-beam caches concatenated for batched beam search)"),
        ("Speed", "JOWA-150M on 7 games: 10.8 FPS without planning, 1.26 FPS with beam search (H = 2, K = 2-4), 0.12 FPS with "
                  "MCTS; hardware not stated (authors, Table 5). Pretraining 1.75M steps, 'around 12 days on A100 GPUs', GPU "
                  "count not given"),
        ("Key detail", "Beam search calls the world model K²(H−1)+K times but takes only H forward latencies because beams are "
                       "batched; at H = 2 the released code runs 1 prefill + 2 × 37 = 75 serial transformer passes per action "
                       "[D]; 1.26 FPS ≈ 0.79 s per frame [D] (the paper does not say whether FPS counts decisions or "
                       "emulator frames at frame skip 4)"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2410.00564 Sec. 3 (84×84, 18 actions), Sec. 4.1-4.2 (architecture, Eq. 4-6, beam search cost), Sec. 5 (K = 36, L = 8, H = 2)",
                "arXiv 2410.00564 Table 5 (FPS), Tables 9-12 (VQ-VAE, transformer, Q-head configs), Table 17 (beam widths), Sec. 5 (pretraining about 12 days on A100 GPUs)",
                "github.com/CJReinforce/JOWA src/models/jowa_model.py, transformer.py, kv_caching.py, src/envs/world_model_env.py, src/agent.py, src/utils.py"],
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
        "decoder": {"text": "VQ decoder (CNN) → 84×84 frame", "sub": "decisions stay in token space; imagined frames decoded for fine-tuning data", "tag": "frozen",
                    "short": "VQ decoder (not used in planning)"},
        "loop": "beam search",
    },
    "flow": {
        "below": [{"text": "Frame 84×84 + action + task ID"}],
        "stack": [
            {"box": "VQ-VAE encoder (CNN)", "id": "enc", "style": "teal", "basis": "stated"},
            {"box": "Nearest codebook entry", "id": "vq", "basis": "code"},
            {"box": "Token embedding", "id": "emb", "minor": True, "basis": "stated",
             "side": "Position + task", "side_basis": "stated"},
            {"group": [
                {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"},
                              {"box": "Masked self-attention", "id": "attn", "style": "dark", "basis": "code"}]},
                {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"}, {"box": "Feed forward", "id": "ffn", "basis": "code"}]},
            ], "repeat": "12 ×", "id": "block"},
            {"fanout": [[{"box": "Next-code head", "id": "out", "minor": True, "basis": "stated"}, {"box": "Next code (argmax)", "id": "sample", "basis": "code"}],
                        [{"box": "Reward head", "id": "rew", "terminal": True, "minor": True, "basis": "stated"}],
                        [{"box": "Done head", "terminal": True, "minor": True, "basis": "stated"}],
                        [{"box": "Q-value head", "id": "q", "terminal": True, "basis": "stated"}]]},
        ],
        "above": [{"box": "VQ-VAE decoder (CNN)", "id": "dec", "style": "teal", "basis": "stated"}, {"text": "Imagined next frame 84×84"}],
        "insets": [
            {"for": "ffn", "stack": [{"box": "Linear", "basis": "code"}, {"box": "GELU", "basis": "code"}, {"box": "Linear", "basis": "code"}]},
            {"for": "q", "label": "Q-value head", "stack": [{"box": "Linear, LayerNorm, Mish", "basis": "code"}, {"box": "Linear, LayerNorm, Mish", "basis": "code"}, {"box": "Linear → return bins", "basis": "code"}]},
        ],
        "annotations": [
            {"at": "vq", "text": "*36* codes per frame · vocabulary of *2,048*", "side": "left", "key": True},
            {"at": "emb", "text": "Embedding dimension of *768*", "side": "left"},
            {"at": "attn", "text": "*12* heads · context of *296* tokens", "side": "left"},
            {"at": "block", "text": "*12* layers · *150M* parameters", "side": "left", "key": True},
            {"at": "sample", "text": "*37* serial passes per imagined frame", "side": "left", "key": True},
            {"at": "q", "text": "*10.8* FPS · *1.26* FPS with planning", "side": "right", "key": True},
        ],
        "feedback": "next step",
    },
    "audit": {"date": "2026-10-23", "checked": 50, "stated": 24, "code": 25, "derived": 1, "assumed": 0, "fixed": 8},
}
