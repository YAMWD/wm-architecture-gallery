MODEL = {
    "slug": "self_forcing",
    "name": "Self Forcing",
    "year": 2025, "month": 6,
    "org": "Adobe Research and UT Austin",
    "family": "dit",
    "role": "Diffusion transformer",
    "status": "NeurIPS 2025 (spotlight)",
    "params": "1.3B (Wan2.1-T2V-1.3B)",
    "params_num": 1.3e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2506.08009", "code": "https://github.com/guandeh17/Self-Forcing"},
    "tagline": "Few-step causal Wan DiT trained on its own rollouts",
    "summary": "The few-step self-rollout recipe later reused by Matrix-Game 2.0, LongLive and SANA-WM. "
               "It converts the bidirectional Wan2.1-T2V-1.3B flow-matching DiT into a block-causal autoregressive "
               "model, trains it by rolling out its own few-step generations with a KV cache and matching the teacher's "
               "distribution (DMD), and at inference keeps a KV cache of past chunks (21 latent frames in the released "
               "code, rolled for longer videos). It is text-to-video "
               "only, with no action input. The authors report 17 FPS at 832x480 on one H100 with 0.69 s first-frame latency.",
    "facts": [
        ("Representation", "Wan2.1 causal 3D VAE latents (stride 4x8x8, 16 channels): an 832x480 frame becomes a 60x104 "
                           "latent; patch (1,2,2) → 30x52 = 1,560 tokens per latent frame [D]; 81 frames = 21 latent frames"),
        ("Core", "Wan2.1-T2V-1.3B DiT: 30 layers, d 1536, 12 heads of 128, FFN 8960; umT5 text via cross-attention; "
                 "1.3B, unchanged from the base; the 14B model serves only as the frozen DMD teacher"),
        ("Attention", "Block-causal: dense within a 3-latent-frame chunk (4,680 tokens), causal across chunks; context "
                      "21 latent frames = 32,760 tokens; with the KV cache, inference uses dense FlashAttention-3, no mask kernel"),
        ("Actions", "None; text prompt only (umT5 cross-attention, 512-token KV cache per layer)"),
        ("Prediction", "Flow matching distilled with DMD Self Forcing to 4 steps (1000, 750, 500, 250; shift 5); the released "
                       "loop adds 1 pass at timestep 0 per chunk to write clean KV, so 5 DiT passes per 12-frame chunk [D]"),
        ("Decoder", "Wan2.1 VAE decoder → 12 frames per chunk at 832x480; decoding is ≈32% of pipeline time after "
                    "distillation (Flash-VAED Table 9)"),
        ("Memory", "Rolling KV cache of the most recent L frames, oldest evicted (L not given; the released 81-frame code "
                   "uses a fixed 32,760-token = 21-latent-frame cache): O(TL) vs O(L²+TL) for recomputing "
                   "overlaps; ≈6.0 GB for that cache in BF16 at batch 1 [D]; trained not to attend to the first chunk so the rolling cache does not flicker"),
        ("Speed", "17.0 FPS, 0.69 s latency (chunk-wise) and 8.9 FPS, 0.45 s (frame-wise) at 832x480 on one H100 (authors, Table 1); "
                  "16.1 FPS on 10 s videos with the rolling cache vs 4.6 FPS with KV recomputation"),
        ("Key detail", "Steady state ≈202 TFLOP per 12-frame chunk, about 70% of it attention against the 32,760-token cache [D]; "
                       "LongLive and Matrix-Game 2.0 reuse the recipe and also keep a Wan2.1-style 1.3B backbone"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2506.08009 Sec. 3.2-3.4, Sec. 4 (Table 1, rolling KV ablation), App. A",
                "Self-Forcing code: wan/configs/wan_t2v_1_3B.py (30 layers, dim 1536, 12 heads, ffn 8960, patch 1x2x2)",
                "configs/self_forcing_dmd.yaml (denoising_step_list, num_frame_per_block 3, latent 21x16x60x104)",
                "pipeline/causal_inference.py (frame_seq_length 1560, timestep-0 KV refresh pass)",
                "wan/modules/causal_model.py (max_attention_size 32760, local_attn_size, sink_size)",
                "Flash-VAED arXiv 2602.19161 Table 9 (decode share)",
                "LongLive arXiv 2509.22622 Sec. 4; Matrix-Game 2.0 report Sec. 2.3, 5.1 (recipe and backbone reuse)"],
    "figure_variant": "Released 1.3B Wan student: 30x1536, 4 DMD steps plus cache refresh",
    "flow": {
        "below": [{"text": "Gaussian noise, 3 latent frames"}],
        "stack": [
            {"group": [
                {"box": "Noisy latent chunk", "id": "noisy", "style": "soft", "minor": True, "basis": "stated"},
                {"box": "Patchify 1×2×2", "id": "patch", "minor": True, "basis": "code"},
                {"group": [
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "side": "Timestep emb.",
                                   "basis": "code", "side_basis": "code"},
                                  {"box": "Block-causal attention", "id": "attn", "style": "dark", "side": "3D RoPE",
                                   "basis": "code", "side_basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                    {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"},
                                  {"box": "Cross-attention", "id": "xattn", "side": "umT5 text",
                                   "basis": "code", "side_basis": "code"}]},
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "basis": "code"},
                                  {"box": "Feed forward", "id": "ffn", "basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                ], "repeat": "30 ×", "id": "block"},
                {"box": "Predicted velocity", "id": "vel", "minor": True, "basis": "code"},
                {"box": "Update latents", "id": "upd", "minor": True, "basis": "stated"},
            ], "loop": "4 steps (DMD)", "tint": "grey", "id": "denoise"},
            {"box": "KV-refresh pass", "id": "kv", "minor": True, "basis": "stated"},
        ],
        "above": [{"box": "Wan2.1 VAE decoder", "id": "dec", "style": "teal", "basis": "code"},
                  {"text": "12 frames at 832×480"}],
        "insets": [{"for": "ffn", "stack": [{"box": "Linear", "basis": "code"}, {"box": "GELU", "basis": "code"},
                                            {"box": "Linear", "basis": "code"}]}],
        "annotations": [
            {"at": "block", "text": "*4,680* tokens per chunk of *12* frames", "side": "left", "key": True},
            {"at": "attn", "text": "*12* heads of *128*, window *32,760* tokens", "side": "left", "key": True},
            {"at": "xattn", "text": "*512* text tokens, no action", "side": "left"},
            {"at": "block", "text": "*30* layers · *1.3B* parameters", "side": "right", "key": True},
            {"at": "kv", "text": "*5* passes per chunk · cache ≈*6.0 GB*", "side": "right"},
            {"at": "dec", "text": "*17* fps · *0.69* s latency", "side": "right", "key": True},
        ],
        "feedback": "cached chunk K/V",
        "feedback_from": "kv",
        "feedback_to": "attn",
    },
}
