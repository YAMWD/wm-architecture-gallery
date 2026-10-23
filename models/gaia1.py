MODEL = {
    "slug": "gaia1",
    "name": "GAIA-1",
    "year": 2023, "month": 9,
    "org": "Wayve",
    "family": "token",
    "role": "Discrete-token model",
    "status": "company technical report",
    "params": "6.5B (+2.6B video decoder)",
    "params_num": 6.5e9,
    "open": "closed",
    "links": {"arXiv": "https://arxiv.org/abs/2309.17080"},
    "tagline": "Driving video tokens, decoded one at a time",
    "summary": "A generative world model for driving: a 6.5B causal transformer predicts the next image token over an "
               "interleaved sequence of text, image and action tokens, trained on 4,700 h of London "
               "driving. Each 288x512 frame is 576 discrete tokens from a 0.3B DINO-distilled tokenizer, so one frame "
               "costs 576 serial passes, and a separate 2.6B video diffusion U-Net, not a transformer, turns the tokens "
               "into pixels with 50 DDIM steps. The report says the model does not yet run in real time.",
    "facts": [
        ("Representation", "576 discrete tokens per 288x512 frame (18x32, downsampling 16), vocabulary 8,192, from a 0.3B image tokenizer trained with a DINO distillation loss"),
        ("Core", "6.5B decoder-only transformer with causal masking, width d = 4,096 (shared embedding dimension); layer and "
                 "head counts not disclosed; norms, feed-forward and residual layout not described, "
                 "so the diagram draws only the masked attention layer"),
        ("Attention", "Dense causal attention over 26 frames at 6.25 Hz (4 s): 26 x (32 text + 576 image + 2 action) = 15,860 tokens; FlashAttention v2; sliding window beyond the context"),
        ("Actions", "2 action tokens and 32 T5-large text tokens per step in the interleaved sequence; conditioning tokens are dropped at random in training, giving unconditional, action- and text-conditioned generation"),
        ("Prediction", "Next-token softmax with top-k = 50: 'n forward steps to generate one new image frame', so 576 serial passes per frame; optional classifier-free guidance doubles the evaluations [D]"),
        ("Decoder", "2.6B video diffusion 3D U-Net with factorized space/time attention: 50 DDIM steps per window of 7 frames (2 overlapping context frames), then temporal upsampling 6.25 → 12.5 → 25 Hz"),
        ("Memory", "KV-cache policy not disclosed; context capped at 26 frames with a sliding window for longer rollouts"),
        ("Speed", "Not disclosed; generation 'does not yet run at real-time' (authors). Training: world model 15 days on 64 A100-80GB, tokenizer 4 days on 32, decoder 15 days on 32 = ~1,568 A100-days [D]"),
        ("Key detail", "576 dependent decode steps per frame through 6.5B parameters, then a 50-step diffusion decoder; with "
                       "16-bit weights (precision not disclosed) each step reads 13 GB of weights [D], so decoding at batch 1 "
                       "is bandwidth-bound"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2309.17080 Sec. 2.1-2.4 (tokens, world model, decoder), Sec. 4.1-4.3 (sizes, training), Sec. 5.1-5.2 (sampling, DDIM), Sec. 9 (not real time)"],
    "diagram": {
        "encoder": {"text": "Frame 288x512 → image tokenizer (0.3B)", "sub": "576 tokens per frame (18×32), vocab 8,192, DINO-distilled",
                    "tag": "frozen", "short": "Image tokenizer, 576 tokens/frame"},
        "tokens": {"groups": [("text", 4, "32 text"), ("frame", 24, "576 image tokens"), ("action", 2, "2 actions")],
                   "note": "per frame at 6.25 Hz; 26 frames = 15,860 tokens"},
        "core": {"title": "Transformer 6.5B · layers not disclosed",
                 "rows": [("attn", "Causal self-attention over all tokens"),
                          ("mlp", "MLP")],
                 "notes": ["context 26 frames = 15,860 tokens; FlashAttention v2", "sliding window for longer rollouts"]},
        "sampling": {"kind": "ar", "text": "Next-token softmax, top-k 50", "sub": "576 serial passes per frame",
                     "short": "Next token, 576 passes per frame"},
        "decoder": {"text": "Video diffusion U-Net (2.6B) → 288x512", "sub": "50 DDIM steps per 7-frame window; 6.25 → 25 Hz upsampling; not a transformer",
                    "tag": "frozen", "short": "Diffusion U-Net, 50 DDIM steps"},
        "loop": "AR rollout",
    },
    "flow": {
        "below": [{"text": "Frame 288×512 + text + action"}],
        "stack": [
            {"box": "U-Net image tokenizer", "short": "Image tokenizer", "id": "tok", "style": "teal", "basis": "stated"},
            {"box": "Nearest codebook entry", "id": "vq", "minor": True, "basis": "stated"},
            {"box": "Interleave tokens", "id": "seq", "side": "T5 text + action", "basis": "stated", "side_basis": "stated"},
            {"group": [
                {"box": "Space-time position emb.", "id": "emb", "minor": True, "basis": "stated"},
                {"group": [
                    {"box": "Masked self-attention", "id": "attn", "style": "dark", "basis": "stated"},
                    {"box": "Rest of block not stated", "id": "rest", "style": "soft", "basis": "stated"},
                ], "repeat": "N ×", "id": "block", "basis": "stated"},
                {"box": "Sample next image token", "short": "Sample next token", "id": "sample", "basis": "stated"},
            ], "loop": "next image token", "loop_short": "next token", "tint": "grey", "id": "ar", "basis": "stated"},
        ],
        "above": [{"box": "Diffusion U-Net decoder", "id": "dec", "style": "soft", "basis": "stated"},
                  {"text": "Frames 288×512 at 25 Hz"}],
        "annotations": [
            {"at": "tok", "text": "*576* tokens per frame, vocabulary *8,192*", "side": "left", "key": True},
            {"at": "seq", "text": "*32* text + *2* action tokens per frame", "side": "left"},
            {"at": "attn", "text": "Context of *26* frames = *15,860* tokens", "side": "left"},
            {"at": "block", "text": "*6.5B* parameters; layers not disclosed", "side": "right", "key": True},
            {"at": "sample", "text": "*576* serial passes per frame", "side": "right", "key": True},
            {"at": "dec", "text": "*2.6B* U-Net, *50* DDIM steps per *7* frames", "side": "left", "key": True},
        ],
    },
    "audit": {"date": "2026-10-23", "checked": 40, "stated": 32, "code": 0, "derived": 3, "assumed": 0, "removed": 5, "fixed": 5},
}
