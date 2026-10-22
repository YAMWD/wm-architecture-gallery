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
    "summary": "The distillation recipe behind most real-time game world models (Matrix-Game 2.0, LongLive, SANA-WM). "
               "It converts the bidirectional Wan2.1-T2V-1.3B flow-matching DiT into a block-causal autoregressive "
               "model, trains it by rolling out its own 4-step generations with a KV cache and matching the teacher's "
               "distribution (DMD), and keeps a rolling KV cache of 21 latent frames at inference. It is text-to-video "
               "only, with no action input. The authors report 17 FPS at 832x480 on one H100 with 0.69 s first-frame latency.",
    "facts": [
        ("Representation", "Wan2.1 causal 3D VAE latents (stride 4x8x8, 16 channels); patch (1,2,2) → 1,560 tokens per "
                           "30x52 latent frame at 832x480 [D]; 81 frames = 21 latent frames"),
        ("Core", "Wan2.1-T2V-1.3B DiT: 30 layers, d 1536, 12 heads of 128, FFN 8960; umT5 text via cross-attention; "
                 "1.3B, unchanged from the base; the 14B model serves only as the frozen DMD teacher"),
        ("Attention", "Block-causal: dense within a 3-latent-frame chunk (4,680 tokens), causal across chunks; context "
                      "21 latent frames = 32,760 tokens; with the KV cache, inference uses dense FlashAttention-3, no mask kernel"),
        ("Actions", "None; text prompt only (umT5 cross-attention, 512-token KV cache per layer)"),
        ("Prediction", "Flow matching distilled with DMD Self Forcing to 4 steps (1000, 750, 500, 250; shift 5); the released "
                       "loop adds 1 pass at timestep 0 per chunk to write clean KV, so 5 DiT passes per 12-frame chunk [D]"),
        ("Decoder", "Wan2.1 VAE decoder → 12 frames per chunk at 832x480; decoding is ≈32% of pipeline time after "
                    "distillation (Flash-VAED Table 9)"),
        ("Memory", "Rolling KV cache of the most recent 21 latent frames, oldest evicted: O(TL) vs O(L²+TL) for recomputing "
                   "overlaps; ≈6.0 GB in BF16 at batch 1 [D]; trained not to attend to the first chunk so the rolling cache does not flicker"),
        ("Speed", "17.0 FPS, 0.69 s latency (chunk-wise) and 8.9 FPS, 0.45 s (frame-wise) at 832x480 on one H100 (authors, Table 1); "
                  "16.1 FPS on 10 s videos with the rolling cache vs 4.6 FPS with KV recomputation"),
        ("Key detail", "Steady state ≈202 TFLOP per 12-frame chunk, about 70% of it attention against the 32,760-token cache [D]; "
                       "the recipe, not the backbone, is what later world models reuse"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2506.08009 Sec. 3.2-3.4, Sec. 4 (Table 1, rolling KV ablation), App. A",
                "Self-Forcing code: wan/configs/wan_t2v_1_3B.py (30 layers, dim 1536, 12 heads, ffn 8960, patch 1x2x2)",
                "configs/self_forcing_dmd.yaml (denoising_step_list, num_frame_per_block 3, latent 21x16x60x104)",
                "pipeline/causal_inference.py (frame_seq_length 1560, timestep-0 KV refresh pass)",
                "wan/modules/causal_model.py (max_attention_size 32760, local_attn_size, sink_size)",
                "Flash-VAED arXiv 2602.19161 Table 9 (decode share)"],
    "diagram": {
        "encoder": {"text": "Frames → Wan2.1 3D causal VAE", "sub": "1,560 latents per 30x52 latent frame", "tag": "frozen",
                    "short": "Wan2.1 3D VAE → 1,560 latents"},
        "tokens": {"groups": [("latent", 24, "4,680 latents per chunk")],
                   "note": "window 21 latent frames = 32,760 tokens"},
        "core": {"title": "Wan2.1 DiT ×30 · d 1536 · 12 heads",
                 "rows": [("attn", "Block-causal self-attention, 3D RoPE"),
                          ("xattn", "Cross-attention to umT5 text"),
                          ("note", "no action input: text-to-video only"),
                          ("mlp", "MLP (FFN 8960)")],
                 "notes": ["rolling KV cache: 21 latent frames, oldest evicted"]},
        "sampling": {"kind": "diffusion", "text": "DMD Self Forcing, 4 denoising steps + 1 KV-refresh pass",
                     "sub": "per chunk of 12 frames (3 latent frames)", "short": "4 steps + 1 KV pass per chunk"},
        "decoder": {"text": "Wan VAE decoder → 12 frames at 832x480", "tag": "frozen", "short": "Wan VAE decoder → 12 frames"},
        "loop": "AR rollout",
    },
    "flow": {
        "below": [{"text": "Text prompt + previous chunks"}],
        "stack": [
            {"box": "Wan2.1 VAE encoder", "id": "vae", "style": "teal"},
            {"box": "Patchify 1×2×2", "id": "patch", "minor": True},
            {"group": [
                {"box": "Noisy latent chunk", "id": "noisy", "style": "soft", "minor": True},
                {"group": [
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "side": "Timestep emb."},
                                  {"box": "Block-causal attention", "id": "attn", "style": "dark", "side": "3D RoPE"}]},
                    {"residual": [{"box": "Cross-attention", "id": "xattn", "side": "umT5 text"}]},
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True}, {"box": "Feed forward", "id": "ffn"}]},
                ], "repeat": "30 ×", "id": "block"},
                {"box": "Predicted velocity", "id": "vel", "minor": True},
                {"box": "Update latents", "id": "upd", "minor": True},
            ], "loop": "4 steps (DMD)", "tint": "grey", "id": "denoise"},
            {"box": "KV-refresh pass", "id": "kv", "minor": True},
        ],
        "above": [{"box": "Wan2.1 VAE decoder", "id": "dec", "style": "teal"}, {"text": "12 frames at 832×480"}],
        "insets": [{"for": "ffn", "stack": [{"box": "Linear"}, {"box": "GELU"}, {"box": "Linear"}]}],
        "annotations": [
            {"at": "vae", "text": "*4,680* tokens per chunk of *12* frames", "side": "left", "key": True},
            {"at": "attn", "text": "*12* heads of *128*, window *32,760* tokens", "side": "left", "key": True},
            {"at": "xattn", "text": "*512* text tokens, no action", "side": "left"},
            {"at": "block", "text": "*30* layers · *1.3B* parameters", "side": "right", "key": True},
            {"at": "kv", "text": "*5* passes per chunk · cache ≈*6.0 GB*", "side": "right"},
            {"at": "dec", "text": "*17* fps · *0.69* s latency", "side": "right", "key": True},
        ],
        "feedback": "next chunk",
    },
}
