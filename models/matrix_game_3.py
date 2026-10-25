MODEL = {
    "slug": "matrix_game_3",
    "name": "Matrix-Game 3.0",
    "year": 2026, "month": 4,
    "org": "Skywork AI",
    "family": "dit",
    "role": "Diffusion transformer",
    "status": "company technical report (arXiv), v3 Sep 2026",
    "params": "5B nominal (≈6.5B checkpoint); 28B MoE scale-up",
    "params_num": 5e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2604.08995", "code": "https://github.com/SkyworkAI/Matrix-Game"},
    "tagline": "Bidirectional segment DiT with retrieved memory",
    "summary": "Skywork's 720p successor to Matrix-Game 2.0, built on Wan2.2-TI2V-5B. Unlike its predecessor it keeps a "
               "bidirectional DiT: each streaming segment denoises 10 new latent frames jointly with 4 past latents and 5 "
               "memory latents retrieved by camera pose and frustum overlap, all in one self-attention sequence with no KV "
               "cache. Multi-segment DMD distils it to 3 steps. The reported ~40 FPS at 720p needs 8 GPUs for the DiT plus "
               "1 for the VAE, INT8 attention projections, a 75%-pruned decoder and GPU-side retrieval (company claim).",
    "facts": [
        ("Representation", "Wan2.2 VAE (4x16x16) + 1x2x2 patchify; a 704x1280 frame becomes a 44x80 latent and a 22x40 grid of "
                           "880 tokens per latent frame [D]; one latent frame = 4 video frames (the first latent holds 1); 10 latent "
                           "frames per segment = 40 video frames (first segment 57)"),
        ("Core", "Wan2.2-TI2V-5B DiT (30 layers, d 3072, 24 heads, FFN 14336 per the HF config); action modules in the first 15 blocks "
                 "as in Matrix-Game 2.0; teacher and student share one bidirectional architecture; a 28B MoE scale-up is also trained"),
        ("Attention", "Bidirectional within a segment: 5 retrieved memory latents + 4 past latents + 10 noisy current latents in one "
                      "sequence (first segment: reference latent + 14 noisy latents), ≈16,720 tokens per segment [D]; head-wise "
                      "perturbed RoPE bases; no KV cache"),
        ("Actions", "Keyboard actions through a dedicated cross-attention module, mouse signals through self-attention (Matrix-Game 2.0 "
                    "design), in blocks 1-15; relative Plücker cues encode the camera geometry between the target and the retrieved memory; "
                    "in every block a Plücker-driven scale/shift (four 3072x3072 layers per block; camera layers total ≈1.17B params in the checkpoint [D]) "
                    "modulates the tokens after self-attention"),
        ("Prediction", "Flow matching; multi-segment self-rollout DMD (1-6 segments, memory from an online pool) → 3 distilled steps per "
                       "segment; error collection and injection train the model on its own imperfect histories"),
        ("Decoder", "MG-LightVAE: Wan2.2 decoder with reduced hidden widths (LightX2V-style), 50% or 75% pruned; decode 0.76 → 0.30 → 0.13 s "
                    "per 17-frame 720x1280 clip (PSNR 33.79 → 31.84 → 31.14 dB); runs on its own GPU"),
        ("Memory", "Camera-aware retrieval: each query view takes the past frame with the highest frustum-overlap score (exact on CPU, "
                   "approximate on GPU); the first latent can be kept as a persistent sink; without a KV cache the memory and past tokens "
                   "are re-processed at every step"),
        ("Speed", "~40 FPS at 720p on an asynchronous 8+1 pipeline (8 DiT GPUs + 1 VAE GPU); GPU model not named (results cover "
                  "H-series with FlashAttention 3 and A-series with FlashAttention 2); leave-one-out Table 1: 27.38 FPS without INT8, "
                  "25.79 without MG-LightVAE, 6.60 with CPU retrieval; single-node 7+1 'slightly lower' (company claim); 3.1 one-minute "
                  "videos/hour on 8 H100s in SANA-WM's benchmark (third party; Matrix-Game 3.0's multi-step, undistilled AR setting, "
                  "not the 3-step real-time pipeline); the ~40 FPS figure is a company claim"),
        ("Key detail", "Real time is a systems result: 9 GPUs, INT8 on the attention projections only (+46% [D]), a decoder the authors "
                       "report as up to 5.2x faster (Table 2 decode times imply ≈5.8x [D]) (+55% [D]) and GPU retrieval (≈6.1x [D]); "
                       "the authors say VAE decode is the bottleneck once the DiT is optimized"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2604.08995 Sec. 3.1 (base model, action injection), 3.2 (memory), 3.3 (multi-segment DMD), 3.4 and "
                "Tables 1-2 (real-time inference, MG-LightVAE), 5.1 (implementation), 5.2.3 (throughput)",
                "Official code SkyworkAI/Matrix-Game (Matrix-Game-3): wan/configs/config.py, wan/modules/model.py, "
                "wan/modules/action_module.py, pipeline/inference_interactive_pipeline.py; HF checkpoint config.json",
                "HF Wan-AI/Wan2.2-TI2V-5B config.json (30 layers, dim 3072, 24 heads, ffn 14336)",
                "SANA-WM arXiv 2605.15178 Sec. 5.2, Table 2 (3.1 videos/hour on 8 H100s)"],
    "figure_variant": "Released Wan2.2-based 30x3072 student with retrieved memory, 3 steps",
    "flow": {
        "below": [{"text": "Frames + keys/mouse + text"}],
        "stack": [
            {"box": "Wan2.2 VAE encoder", "id": "vae", "style": "teal", "basis": "code"},
            {"box": "Patchify 2×2", "id": "patch", "minor": True, "basis": "code"},
            {"box": "Camera-aware retrieval", "id": "mem", "minor": True, "side": "Camera poses", "basis": "stated", "side_basis": "stated"},
            {"group": [
                {"box": "Noisy + past + memory", "id": "seq", "style": "soft", "minor": True, "basis": "stated"},
                {"group": [
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "side": "Timestep emb.", "basis": "code", "side_basis": "code"},
                                  {"box": "Bidirectional attention", "id": "attn", "style": "dark", "side": "Perturbed RoPE", "basis": "stated", "side_basis": "stated"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                    {"box": "Camera scale, shift", "id": "cam", "minor": True, "side": "Plücker rays", "basis": "code", "side_basis": "code"},
                    {"box": "LayerNorm", "minor": True, "basis": "code"},
                    {"residual": [{"box": "Cross-attention", "id": "xattn", "side": "Text emb.", "basis": "code", "side_basis": "code"}]},
                    {"box": "Action module", "id": "act", "style": "orange", "side": "Keys + mouse", "basis": "stated", "side_basis": "stated"},
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "basis": "code"},
                                  {"box": "Feed forward", "id": "ffn", "basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                ], "repeat": "30 ×", "id": "block", "basis": "code"},
                {"box": "Predicted velocity", "id": "vel", "minor": True, "basis": "stated"},
                {"box": "Update latents", "id": "upd", "minor": True, "basis": "code"},
            ], "loop": "3 steps (DMD)", "tint": "grey", "id": "denoise", "basis": "code"},
        ],
        "above": [{"box": "MG-LightVAE decoder", "id": "dec", "style": "teal", "basis": "stated"}, {"text": "≈40 frames per segment at 720p"}],
        "insets": [{"for": "act", "label": "action module", "stack": [{"box": "Mouse → self-attention", "basis": "stated"},
                                                                     {"box": "Keys → cross-attention", "basis": "stated"}]}],
        "annotations": [
            {"at": "seq", "text": "*16,720* tokens, re-run every step", "side": "right"},
            {"at": "attn", "text": "*5* memory + *4* past + *10* noisy latents", "side": "left", "key": True},
            {"at": "act", "text": "Action modules in *15* of *30* blocks", "side": "left"},
            {"at": "ffn", "text": "Width *3,072*, hidden *14,336*", "side": "left"},
            {"at": "block", "text": "*30* layers · *24* heads · ≈*6.5B*", "side": "right", "key": True},
            {"at": "dec", "text": "~*40* fps at *720p*", "side": "right", "key": True},
        ],
        "feedback": "segment latents",
        "feedback_from": "upd",
        "feedback_to": "seq",
    },
}
