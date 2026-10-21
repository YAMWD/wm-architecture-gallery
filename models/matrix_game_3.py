MODEL = {
    "slug": "matrix_game_3",
    "name": "Matrix-Game 3.0",
    "year": 2026, "month": 4,
    "org": "Skywork AI",
    "family": "dit",
    "role": "Diffusion transformer",
    "status": "company technical report (arXiv), v3 Sep 2026",
    "params": "5B (28B MoE scale-up)",
    "params_num": 5e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2604.08995", "code": "https://github.com/SkyworkAI/Matrix-Game"},
    "summary": "Skywork's 720p successor to Matrix-Game 2.0, built on Wan2.2-TI2V-5B. Unlike its predecessor it keeps a "
               "bidirectional DiT: each streaming segment denoises 10 new latent frames jointly with 4 past latents and 5 "
               "memory latents retrieved by camera pose and frustum overlap, all in one self-attention sequence with no KV "
               "cache. Multi-segment DMD distils it to 3 steps. The reported ~40 FPS at 720p needs 8 GPUs for the DiT plus "
               "1 for the VAE, INT8 attention projections, a 75%-pruned decoder and GPU-side retrieval (company claim).",
    "facts": [
        ("Representation", "Wan2.2 VAE (4x16x16) + patchify; 880 tokens per 22x40 latent frame at 704x1280 if the patch is (1,2,2) "
                           "as in Wan2.2 [D, assumption]; one latent frame = 4 video frames"),
        ("Core", "Wan2.2-TI2V-5B DiT (30 layers, d 3072, 24 heads, FFN 14336 per the HF config); action modules in the first 15 blocks "
                 "as in Matrix-Game 2.0; teacher and student share one bidirectional architecture; a 28B MoE scale-up is also trained"),
        ("Attention", "Bidirectional within a segment: 5 retrieved memory latents + 4 past latents + 10 noisy current latents in one "
                      "sequence (first segment: reference latent + 14 noisy latents), ≈16,720 tokens per segment [D]; head-wise "
                      "perturbed RoPE bases; no KV cache"),
        ("Actions", "Keyboard actions through a dedicated cross-attention module, mouse signals through self-attention (Matrix-Game 2.0 "
                    "design), in blocks 1-15; relative Plücker cues encode the camera geometry between the target and the retrieved memory"),
        ("Prediction", "Flow matching; multi-segment self-rollout DMD (1-6 segments, memory from an online pool) → 3 distilled steps per "
                       "segment; error collection and injection train the model on its own imperfect histories"),
        ("Decoder", "MG-LightVAE: Wan2.2 decoder with reduced hidden widths (LightX2V-style), 50% or 75% pruned; decode 0.76 → 0.30 → 0.13 s "
                    "per 17-frame 720x1280 clip (PSNR 33.79 → 31.84 → 31.14 dB); runs on its own GPU"),
        ("Memory", "Camera-aware retrieval: each query view takes the past frame with the highest frustum-overlap score (exact on CPU, "
                   "approximate on GPU); the first latent can be kept as a persistent sink; without a KV cache the memory and past tokens "
                   "are re-processed at every step"),
        ("Speed", "~40 FPS at 720p on an asynchronous 8+1 pipeline (8 DiT GPUs + 1 VAE GPU), GPU model not named (H-series with "
                  "FlashAttention 3); leave-one-out Table 1: 27.38 FPS without INT8, 25.79 without MG-LightVAE, 6.60 with CPU retrieval; "
                  "single-node 7+1 'slightly lower' (company claim); 3.1 one-minute videos/hour on 8 H100s in SANA-WM's benchmark (third party, config unstated)"),
        ("Key detail", "Real time is a systems result: 9 GPUs, INT8 on the attention projections only (+46%), a 5.85x faster decoder (+55%) "
                       "and GPU retrieval (≈6.1x); the authors say VAE decode is the bottleneck once the DiT is optimized"),
    ],
    "evidence": "read",
    "sources": ["verified_findings.md Findings 13-14 (8+1 pipeline, Table 1 FPS, Table 2 VAE times, INT8 scope, 3 steps)",
                "arXiv 2604.08995 Sec. 3.1 (base model, action injection), 3.2 (memory), 3.3 (multi-segment DMD), 3.4 (real-time "
                "inference), 5.1 (implementation: 4 past + 10 current + 5 memory latents), 5.2.3",
                "HF Wan-AI/Wan2.2-TI2V-5B config.json (local copy: 30 layers, dim 3072, 24 heads, ffn 14336)",
                "SANA-WM arXiv 2605.15178 Table 2 (3.1 videos/hour on 8 H100s)"],
    "diagram": {
        "encoder": {"text": "Frames → Wan2.2 VAE (4x16x16) + patchify", "sub": "880 latents per 22x40 latent frame at 704x1280 [D]",
                    "short": "Wan2.2 VAE → 880 latents"},
        "tokens": {"groups": [("latent", 10, "10 noisy latents"), ("latent", 9, "4 past + 5 memory latents")],
                   "note": "per segment ≈16,720 tokens; no KV cache"},
        "core": {"title": "Wan2.2 DiT ×30 · d 3072 · 24 heads",
                 "rows": [("attn", "Bidirectional attention over segment"),
                          ("xattn", "Keyboard actions via cross-attention"),
                          ("action", "Mouse signals via self-attention"),
                          ("mlp", "MLP (FFN 14336)")],
                 "notes": ["action modules in blocks 1-15 (Matrix-Game 2.0 design)",
                           "memory + past + current latents re-run every step: no KV cache",
                           "camera-aware retrieval by frustum overlap, on the GPU"]},
        "sampling": {"kind": "diffusion", "text": "Multi-segment DMD, 3 denoising steps", "sub": "per segment of 10 latent frames (≈40 frames [D])",
                     "short": "3 steps per segment"},
        "decoder": {"text": "MG-LightVAE (75% pruned) → 720p, on its own GPU", "sub": "0.13 s per 17-frame clip vs 0.76 s stock",
                    "short": "MG-LightVAE decoder → 720p"},
        "loop": "AR rollout",
    },
}
