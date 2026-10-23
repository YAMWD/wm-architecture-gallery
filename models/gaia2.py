MODEL = {
    "slug": "gaia2",
    "name": "GAIA-2",
    "year": 2025, "month": 3,
    "org": "Wayve",
    "family": "driving",
    "role": "Diffusion transformer",
    "status": "company technical report (arXiv 2503.20523)",
    "params": "8.4B + 285M tokenizer",
    "params_num": 8.4e9,
    "open": "closed",
    "links": {"arXiv": "https://arxiv.org/abs/2503.20523", "page": "https://wayve.ai/thinking/gaia-2/"},
    "tagline": "Factorized-attention DiT over five cameras",
    "summary": "Wayve's multi-camera driving world model: a video tokenizer with 32x spatial and 8x temporal compression turns "
               "up to 5 camera streams into 64-channel latents, and an 8.4B space-time factorized transformer denoises them "
               "with flow matching. The ego action and flow-matching time enter through adaptive LayerNorm; 3D agent boxes, "
               "scene and road-layout metadata and CLIP or scenario embeddings through cross-attention; camera geometry and "
               "timestamps as added encodings. It runs 50 denoising steps; Wayve describes no KV cache, reports no inference "
               "speed and lists distillation and faster, near-real-time synthesis as future work.",
    "facts": [
        ("Representation", "Video tokenizer (space-time factorized transformer, 85M encoder / 200M decoder): 8x temporal, 32x spatial, "
                           "64 channels; 24 frames at 448x960 → 3x14x30 latents (≈400x compression); 420 latents per camera per latent "
                           "step, 2,100 across 5 cameras [D]"),
        ("Core", "22 space-time factorized transformer blocks, d 4096, 32 heads, 8.4B parameters; each block adds the position, "
                 "timestamp and camera encodings, then runs spatial attention (over space and cameras), temporal attention, "
                 "cross-attention and an MLP with adaptive LayerNorm; QK-norm before each attention. Assumed in the diagram "
                 "(not described): adaptive LayerNorm before each attention layer and the residual connections, as in DiT"),
        ("Attention", "Factorized: spatial attention over 2,100 tokens (5 cameras × 420) [D], temporal attention over 6 latent steps; "
                      "training window 48 frames × 5 cameras = 12,600 tokens; no full 3D attention; sinusoidal space and "
                      "timestamp encodings plus learned camera geometry, re-added at the start of every block"),
        ("Actions", "Ego-vehicle action (speed, curvature) and flow-matching time via adaptive LayerNorm in every block (found more "
                    "accurate than cross-attention); 3D agent boxes, metadata (incl. road layout) and CLIP or scenario embeddings "
                    "via cross-attention; camera geometry and timestamps are added to the latents with the positional encodings"),
        ("Prediction", "Flow matching, 50 denoising steps, linear-quadratic schedule, no distillation; CFG off by default (scale 2-20 "
                       "for hard cases); rollout in latent space: k=3 context latents, predict the next set of latents (3 per "
                       "stride in Fig. 2), append, slide the window"),
        ("Decoder", "200M decoder with 24 space-time factorized blocks (16 + 8, d 512, 16 heads): jointly decodes 3 latent steps "
                    "into 24 frames at 448x960 per camera; sliding window at inference"),
        ("Memory", "Sliding window of latents; no KV cache described"),
        ("Speed", "Not disclosed; 'real-time or near-real-time video synthesis remains computationally intensive', distillation listed "
                  "as future work (authors); ≈1.1e16 dense FLOPs per 50-step, 48-frame, 5-camera window [D]"),
        ("Key detail", "Wayve chose 32x spatial / 64-channel latents because shorter latent sequences give faster inference and "
                       "better memory efficiency, and the model captures dynamics better; ≈1.5e12 training tokens on 256 H100s [D]"),
    ],
    "evidence": "read",
    "sources": ["GAIA-2 technical report, arXiv 2503.20523v1: Sec. 2.1 tokenizer (85M/200M, 8x/32x, 64 ch), 2.2 world model "
                "(22 blocks, C=4096, 32 heads, conditioning), 4 training (12,600 tokens, 256 H100), 5 inference (50 steps, k=3, "
                "CFG), 8 future work; Fig. 2, Fig. 3",
                "Wayve GAIA-2 page, https://wayve.ai/thinking/gaia-2/"],
    "diagram": {
        "encoder": {"text": "5 cameras 448x960 → video tokenizer (85M)", "sub": "8x temporal, 32x spatial, 64 ch; 420 latents per camera per step",
                    "tag": "frozen", "short": "Video tokenizer → 420 latents/camera"},
        "tokens": {"groups": [("latent", 24, "2,100 latents (5 cameras)")],
                   "note": "per latent step; 6 steps = 12,600 tokens"},
        "core": {"title": "Space-time transformer ×22 · d 4096 · 32 heads",
                 "rows": [("attn", "Spatial attention: space + cameras"),
                          ("attn", "Temporal attention over latent steps"),
                          ("xattn", "Cross-attn to agents and metadata"),
                          ("action", "Ego action + time → adaptive LN"),
                          ("mlp", "MLP")],
                 "notes": ["QK-norm; context k=3 latent steps, sliding window; no KV cache described"]},
        "sampling": {"kind": "diffusion", "text": "Flow matching, 50 steps, linear-quadratic schedule", "sub": "no distillation; CFG off by default",
                     "short": "Flow matching, 50 steps"},
        "decoder": {"text": "Tokenizer decoder (200M) → 24 frames at 448x960", "sub": "per camera; 3 latents decoded jointly, sliding window",
                    "tag": "frozen", "short": "Decoder (200M) → 24 frames"},
        "loop": "AR rollout",
    },
    "flow": {
        "below": [{"text": "5 cameras 448×960 + ego action"}],
        "stack": [
            {"box": "Video tokenizer encoder", "short": "Video tokenizer", "id": "tok", "style": "teal", "basis": "stated"},
            {"group": [
                {"box": "Noisy + context latents", "id": "noisy", "style": "soft", "minor": True, "basis": "stated"},
                {"group": [
                    {"box": "Positions + camera emb.", "id": "pos", "minor": True, "basis": "stated"},
                    {"residual": [{"box": "Adaptive LayerNorm", "id": "ada", "minor": True, "basis": "assumed"},
                                  {"box": "Space + camera attention", "short": "Spatial attention", "id": "sattn", "style": "dark",
                                   "basis": "stated"}]},
                    {"residual": [{"box": "Adaptive LayerNorm", "minor": True, "basis": "assumed"},
                                  {"box": "Temporal attention", "id": "tattn", "style": "dark", "basis": "stated"}]},
                    {"residual": [{"box": "Adaptive LayerNorm", "minor": True, "basis": "assumed"},
                                  {"box": "Cross-attention", "id": "xattn", "side": "Agents + metadata", "basis": "stated",
                                   "side_basis": "stated"}]},
                    {"residual": [{"box": "Adaptive LayerNorm", "side": "Ego action + time", "basis": "stated",
                                   "side_basis": "stated"},
                                  {"box": "MLP", "id": "mlp", "minor": True, "basis": "stated"}]},
                ], "repeat": "22 ×", "id": "block", "basis": "assumed"},
                {"box": "Predicted velocity", "id": "vel", "minor": True, "basis": "stated"},
                {"box": "Update latents", "id": "upd", "minor": True, "basis": "stated"},
            ], "loop": "50 denoising steps", "tint": "grey", "id": "denoise", "basis": "stated"},
        ],
        "above": [{"box": "Video tokenizer decoder", "id": "dec", "style": "teal", "basis": "stated"},
                  {"text": "24 frames × 5 cameras at 448×960"}],
        "annotations": [
            {"at": "tok", "text": "≈*2,100* latents per step over *5* cameras", "side": "left", "key": True},
            {"at": "sattn", "text": "*32* heads, width *4,096*", "side": "left"},
            {"at": "tattn", "text": "Window of *6* latent steps, *12,600* tokens", "side": "left"},
            {"at": "block", "text": "*50* passes per *3* new latents, *8.4B* parameters", "side": "right", "key": True},
            {"at": "dec", "text": "Speed not disclosed; *200M* decoder", "side": "right", "key": True},
        ],
        "feedback": "next set of latents",
    },
    "audit": {"date": "2026-10-22", "checked": 47, "stated": 34, "code": 1, "derived": 5, "assumed": 7, "fixed": 10},
}
