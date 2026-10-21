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
    "summary": "Wayve's multi-camera driving world model: a video tokenizer with 32x spatial and 8x temporal compression turns "
               "5 camera streams into 64-channel latents, and an 8.4B space-time factorized transformer denoises them with "
               "flow matching, conditioned on the ego action through adaptive LayerNorm and on agents, maps and scene "
               "metadata through cross-attention. It runs 50 denoising steps with no distillation and no KV cache; Wayve "
               "reports no inference speed and calls real-time synthesis future work.",
    "facts": [
        ("Representation", "Video tokenizer (space-time factorized transformer, 85M encoder / 200M decoder): 8x temporal, 32x spatial, "
                           "64 channels; 24 frames at 448x960 → 3x14x30 latents (≈400x compression); 420 latents per camera per latent "
                           "step, 2,100 across 5 cameras [D]"),
        ("Core", "22 space-time factorized transformer blocks, d 4096, 32 heads; each block: spatial attention (over space and cameras), "
                 "temporal attention, cross-attention, MLP with adaptive LayerNorm; QK-norm; 8.4B parameters trained from scratch"),
        ("Attention", "Factorized: spatial attention over 2,100 tokens (5 cameras × 420), temporal attention over 6 latent steps; "
                      "training window 48 frames × 5 cameras = 12,600 tokens; no full 3D attention"),
        ("Actions", "Ego-vehicle action and flow-matching time via adaptive LayerNorm in every block (found more accurate than "
                    "cross-attention); agents, metadata, camera parameters and external embeddings via cross-attention"),
        ("Prediction", "Flow matching, 50 denoising steps, linear-quadratic schedule, no distillation; CFG off by default (scale 2-20 "
                       "for hard cases); rollout: k=3 context latents, predict the next latents, append, slide the window"),
        ("Decoder", "200M transformer decoder with full spatiotemporal attention: 3 latent steps → 24 frames at 448x960 per camera, "
                    "decoded with a sliding window"),
        ("Memory", "Sliding window of latents; no KV cache described"),
        ("Speed", "Not disclosed; 'real-time or near-real-time video synthesis remains computationally intensive', distillation listed "
                  "as future work (authors); ≈1.1e16 dense FLOPs per 50-step, 48-frame, 5-camera window [D]"),
        ("Key detail", "Wayve chose 32x spatial / 64-channel latents because shorter sequences give faster inference; an offline "
                       "simulator where throughput, not latency, matters; ≈1.5e12 training tokens on 256 H100s [D]"),
    ],
    "evidence": "read",
    "sources": ["GAIA-2 report (local src/gaia2.txt): Sec. 2.1.1 tokenizer, 2.2 world model (22 blocks, C=4096, 32 heads, adaptive "
                "LayerNorm), 3 training (12,600 tokens, 128/256 H100), 4 inference (50 steps, k=3, CFG), 8 future work",
                "ar_token_and_physical_ai.md Group 2 (derived counts)"],
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
}
